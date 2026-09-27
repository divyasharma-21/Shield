from pathlib import Path
import json, random, re, joblib
import numpy as np, pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import f1_score, classification_report
from sklearn.model_selection import train_test_split

BASE=Path(__file__).resolve().parents[1]; RAW=BASE/'data'/'raw'; MODELS=BASE/'models'; REPORTS=BASE/'reports'
MODELS.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)
CATS=['benign','harassment','threat','coercion_blackmail','secrecy_isolation','unsafe_image_request','location_meetup_risk','financial_scam','remote_access_social_engineering','grooming_risk_pattern']

def variants(cat):
    bank={
'benign':['I will see you after class.','Thanks for helping me with the assignment.','Please call me when you get home.','The group project meeting is at five.','Can you send me the notes from today?','Hope you have a good evening.','Dinner is ready when you are.','Let me know if you need help with the homework.'],
'harassment':['Everyone keeps making fun of you in the group.','You are pathetic and nobody wants you here.','Stop posting embarrassing comments about me.','They keep insulting you in the class chat.','You are being targeted with repeated insults in the group.','People keep sending you humiliating messages.'],
'threat':['I am going to hurt you after school tomorrow.','If you come here again I will hurt you.','You will regret it when I see you tomorrow.','I will find you after class and hurt you.','Do not come near me or I will attack you.'],
'coercion_blackmail':['Send me a private photo now or I will share our private chat.','If you do not pay, I will post the screenshots publicly.','Give me what I asked for or I will expose these messages.','You have ten minutes or I will send the private pictures to everyone.','Do this now or I will tell everyone your secret.'],
'secrecy_isolation':['Do not tell your parents about this conversation.','Keep this secret from your friends and family.','Do not tell anyone that we are talking.','Stay on the call and do not contact your parents.','You do not need to tell anyone else about our messages.'],
'unsafe_image_request':['Send me a private photo of yourself right now.','I want a picture of you that you would not show your parents.','Send me a photo now and do not tell anyone.','Take a private picture and send it to me.'],
'location_meetup_risk':['Send me your live location and meet me alone tonight.','Turn on location sharing and come to this place without telling anyone.','Tell me where you are and meet me after school by yourself.','Keep your location on so I can see where you are.'],
'financial_scam':['You won a prize, just pay a small processing fee now.','Send the money immediately to claim your reward.','Enter your payment PIN to receive the refund.','Your account will be blocked unless you pay today.'],
'remote_access_social_engineering':['Install AnyDesk and give me the screen code so I can fix your account.','Download remote support and share your screen with me.','Install this app and stay on the call while I control your phone.','Give me remote access so I can verify your payment.'],
'grooming_risk_pattern':['You are mature for your age, so keep our chats private.','Do not tell your parents; I understand you better than they do.','You can trust me, but keep our private conversations secret.','You are special to me, send me a private photo and do not tell anyone.']}
    return bank[cat]

rows=[]
# Use the existing reviewed tactic corpus as real project-specific evidence where it overlaps.
p=RAW/'sentrymesh_tactics.csv'
if p.exists():
 d=pd.read_csv(p)
 for _,r in d.iterrows():
  text=str(r.text)
  cat='benign'
  if r.get('fear_or_threat',0): cat='threat'
  if r.get('secrecy',0) or r.get('isolation',0): cat='secrecy_isolation'
  if r.get('remote_access_request',0) or r.get('screen_share_request',0): cat='remote_access_social_engineering'
  if r.get('upi_collect_request',0) or r.get('payment_request',0): cat='financial_scam'
  rows.append((text,cat,'sentrymesh_reviewed'))
# Synthetic safety-domain augmentation. Clearly marked in metadata.
rng=random.Random(42)
for cat in CATS:
 base=variants(cat)
 for i in range(180):
  s=base[i%len(base)]
  prefixes=['','Please ','Listen, ','Just ','Right now, ','Honestly, ']
  suffixes=['',' Please reply.',' Do not ignore me.',' This is important.','']
  rows.append((prefixes[i%len(prefixes)]+s+suffixes[(i*3)%len(suffixes)],cat,'synthetic_augmented'))


# Add real benign communication from public SMS and SentryMesh legitimate corpora as negative safety examples.
for real_path in [RAW/'uci_sms_processed.csv', RAW/'sentrymesh_legitimate_indian.csv']:
 if real_path.exists():
  rd=pd.read_csv(real_path)
  if 'label' in rd.columns: rd=rd[rd['label'].astype(str).str.lower().isin(['legitimate','ham'])]
  for _,rr in rd.sample(n=min(900,len(rd)),random_state=42).iterrows():
   txt=str(rr.get('text','')).strip()
   if txt: rows.append((txt,'benign','real_benign'))
# Real email corpus: only messages already labeled legitimate; sample a modest, reproducible subset.
real_email=RAW/'sentrymesh_real_email.csv'
if real_email.exists():
 rd=pd.read_csv(real_email,usecols=['text','label'])
 rd=rd[rd.label=='legitimate']
 for _,rr in rd.sample(n=min(1200,len(rd)),random_state=42).iterrows():
  txt=str(rr.text).strip()
  if txt: rows.append((txt,'benign','real_benign'))

df=pd.DataFrame(rows,columns=['text','label','source']).drop_duplicates('text').reset_index(drop=True)
Xtr,Xte,ytr,yte=train_test_split(df.text,df.label,test_size=.22,stratify=df.label,random_state=42)
word=TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=40000,sublinear_tf=True)
char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=40000,sublinear_tf=True)
A=word.fit_transform(Xtr); B=char.fit_transform(Xtr); C=word.transform(Xte); D=char.transform(Xte)
model=OneVsRestClassifier(LogisticRegression(max_iter=1200,class_weight='balanced',C=2.0,solver='liblinear',random_state=42))
model.fit(hstack([A,B]),ytr)
p=model.predict_proba(hstack([C,D])); pred=np.array(model.classes_)[p.argmax(axis=1)]
metrics={'model_name':'parentguardian_safety_v1','samples':len(df),'test_samples':len(Xte),'macro_f1':float(f1_score(yte,pred,average='macro')),'classes':CATS,'source_counts':df.source.value_counts().to_dict(),'note':'Synthetic safety augmentation is explicitly labeled; no diagnosis or intent inference is claimed.'}
joblib.dump({'model':model,'word_vectorizer':word,'char_vectorizer':char,'classes':CATS,'model_name':metrics['model_name']},MODELS/'parentguardian_safety_v1.joblib')
(REPORTS/'parentguardian_safety_v1_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
