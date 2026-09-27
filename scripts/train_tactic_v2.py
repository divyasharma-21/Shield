from pathlib import Path
import json,random,joblib
import pandas as pd, numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
BASE=Path(__file__).resolve().parents[1]; RAW=BASE/'data'/'raw'; MODELS=BASE/'models'; REPORTS=BASE/'reports'
TACTICS=['authority_impersonation','urgency','fear_or_threat','secrecy','isolation','payment_request','otp_request','credential_request','remote_access_request','screen_share_request','upi_collect_request']
rows=[]
p=RAW/'sentrymesh_tactics.csv'; df=pd.read_csv(p)
for _,r in df.iterrows(): rows.append((str(r.text),[int(r.get(t,0)) for t in TACTICS]))
# Augment each reviewed row with small formatting-preserving variants; labels remain from the reviewed annotation.
rng=random.Random(42)
for text,y in list(rows):
 for i in range(5):
  v=text.replace('immediately','right now' if i%2 else 'immediately').replace('urgent','urgently' if i%2 else 'urgent')
  if i==1: v='Please '+v
  if i==2: v=v+' Act now.'
  if i==3: v=v.replace('Dear Customer','Hello Customer')
  if i==4: v=v+' [reviewed variant]'
  rows.append((v,y))

# Add real benign communication as all-zero tactic negatives.
for real_path in [RAW/'uci_sms_processed.csv', RAW/'sentrymesh_legitimate_indian.csv']:
 if real_path.exists():
  rd=pd.read_csv(real_path)
  if 'label' in rd.columns: rd=rd[rd.label.astype(str).str.lower().isin(['legitimate','ham'])]
  for _,rr in rd.sample(n=min(1800,len(rd)),random_state=42).iterrows():
   txt=str(rr.get('text','')).strip()
   if txt: rows.append((txt,[0]*len(TACTICS)))
real_email=RAW/'sentrymesh_real_email.csv'
if real_email.exists():
 rd=pd.read_csv(real_email,usecols=['text','label']); rd=rd[rd.label=='legitimate']
 for _,rr in rd.sample(n=min(2200,len(rd)),random_state=42).iterrows():
  txt=str(rr.text).strip()
  if txt: rows.append((txt,[0]*len(TACTICS)))
texts=[x[0] for x in rows]; y=np.array([x[1] for x in rows])
word=TfidfVectorizer(ngram_range=(1,2),min_df=1,max_features=30000,sublinear_tf=True)
char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1,max_features=30000,sublinear_tf=True)
X=hstack([word.fit_transform(texts),char.fit_transform(texts)])
model=MultiOutputClassifier(LogisticRegression(max_iter=1000,class_weight='balanced',C=2,solver='liblinear',random_state=42)).fit(X,y)
joblib.dump({'model':model,'word_vectorizer':word,'char_vectorizer':char,'tactics':TACTICS,'model_name':'sentrymesh_tactic_v2'},MODELS/'tactic_v2.joblib')
(REPORTS/'tactic_v2_metadata.json').write_text(json.dumps({'model_name':'sentrymesh_tactic_v2','samples':len(texts),'source':'sentrymesh_tactics.csv + labeled augmentation','tactics':TACTICS,'warning':'augmentation is not independent real-world validation'},indent=2))
print('saved',len(texts))
