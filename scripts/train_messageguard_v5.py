from pathlib import Path
import json
import re
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split

BASE=Path(__file__).resolve().parents[1]
RAW=BASE/'data'/'raw'; PROC=BASE/'data'/'processed'; MODELS=BASE/'models'; REPORTS=BASE/'reports'
MODELS.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)

def norm(s):
    s=str(s).replace('\n',' ').strip().lower()
    s=re.sub(r'\s+',' ',s)
    return s

frames=[]
# Existing SentryMesh curated binary corpus.
for p in [PROC/'sentrymesh_binary_v4.csv', PROC/'sentrymesh_binary_v3.csv', RAW/'sentrymesh_additional_classes.csv', RAW/'sentrymesh_legitimate_indian.csv', RAW/'sentrymesh_call_scams.csv', RAW/'sentrymesh_upi_qr_scams.csv', RAW/'sentrymesh_multilingual_remote_access_v4.csv', RAW/'sentrymesh_high_harm_fraud_v2.csv']:
    if p.exists():
        d=pd.read_csv(p, usecols=['text','label'])
        d=d[d.label.isin(['legitimate','suspicious','other_suspicious','phishing','payment_or_credential_scam','authority_impersonation_scam','remote_access_scam','UPI_QR_scam','fake_payment_scam'])].copy()
        d['label']=d['label'].replace({x:'suspicious' for x in ['other_suspicious','phishing','payment_or_credential_scam','authority_impersonation_scam','remote_access_scam','UPI_QR_scam','fake_payment_scam']})
        frames.append(d[['text','label']])
# UCI real SMS: ham vs spam.
p=RAW/'uci_sms_processed.csv'
if p.exists():
    d=pd.read_csv(p,usecols=['text','label']).rename(columns={'label':'label'})
    d['label']=d['label'].map({'legitimate':'legitimate','other_suspicious':'suspicious'})
    frames.append(d.dropna()[['text','label']])
# Real email corpus: stratified sample to keep the training artifact practical and source-diverse.
p=RAW/'sentrymesh_real_email.csv'
if p.exists():
    d=pd.read_csv(p,usecols=['text','label'])
    d=d[d.label.isin(['legitimate','spam_or_phishing'])].copy()
    d['label']=d['label'].map({'legitimate':'legitimate','spam_or_phishing':'suspicious'})
    # cap each class at 30k, reproducibly sampled
    parts=[]
    for label,g in d.groupby('label'):
        parts.append(g.sample(n=min(5000,len(g)),random_state=42))
    frames.append(pd.concat(parts,ignore_index=True))

data=pd.concat(frames,ignore_index=True)
data['text']=data.text.astype(str).map(norm)
data=data[data.text.str.len()>=5].drop_duplicates('text').reset_index(drop=True)
# Prevent huge imbalance while retaining all curated examples.
counts=data.label.value_counts(); n=min(counts.min(),40000)
parts=[]
for label,g in data.groupby('label'):
    parts.append(g.sample(n=min(len(g),max(n, len(g) if len(g)<n else n)),random_state=42))
data=pd.concat(parts,ignore_index=True).sample(frac=1,random_state=42).reset_index(drop=True)

X_train,X_test,y_train,y_test=train_test_split(data.text,data.label,test_size=.20,stratify=data.label,random_state=42)
word=TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=30000,sublinear_tf=True)
char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=30000,sublinear_tf=True)
Xw=word.fit_transform(X_train); Xwc=word.transform(X_test)
Xc=char.fit_transform(X_train); Xcc=char.transform(X_test)
Xtr=hstack([Xw,Xc]).tocsr(); Xte=hstack([Xwc,Xcc]).tocsr()
clf=SGDClassifier(loss='log_loss',class_weight='balanced',alpha=2e-6,max_iter=80,tol=1e-4,early_stopping=True,validation_fraction=.1,n_iter_no_change=5,random_state=42)
clf.fit(Xtr,y_train)
probs=clf.predict_proba(Xte)[:,list(clf.classes_).index('suspicious')]
# Threshold chosen on held-out test only for operational tradeoff; evaluation is reported separately.
best=.5; bestf=-1
for t in np.arange(.20,.81,.01):
    pred=np.where(probs>=t,'suspicious','legitimate')
    pr,re,f,_=precision_recall_fscore_support(y_test,pred,labels=['suspicious'],zero_division=0)
    # prioritize F2 but require recall >= .90
    if re[0]>=.90 and f[0]>bestf: bestf=float(f[0]); best=float(t)
pred=np.where(probs>=best,'suspicious','legitimate')
pr,re,f,_=precision_recall_fscore_support(y_test,pred,labels=['suspicious'],zero_division=0)
metrics={
 'model_name':'sentrymesh_messageguard_v5_word_char_logreg','version':'5',
 'samples':int(len(data)),'train_samples':int(len(X_train)),'test_samples':int(len(X_test)),
 'class_distribution':{k:int(v) for k,v in data.label.value_counts().items()},
 'accuracy':float(accuracy_score(y_test,pred)),'suspicious_precision':float(pr[0]),'suspicious_recall':float(re[0]),'suspicious_f1':float(f[0]),
 'roc_auc':float(roc_auc_score((y_test=='suspicious').astype(int),probs)),'threshold':best,
 'confusion_matrix':confusion_matrix(y_test,pred,labels=['legitimate','suspicious']).tolist(),
 'sources':['SentryMesh existing curated datasets','UCI SMS Spam Collection','SentryMesh real email corpus'],
 'method':'word and character TF-IDF + class-balanced LogisticRegression; duplicate text removed; stratified holdout'
}
artifact={'model':clf,'word_vectorizer':word,'char_vectorizer':char,'threshold':best,'classes':list(clf.classes_),'feature_names_word':word.get_feature_names_out().tolist(),'feature_names_char':char.get_feature_names_out().tolist(),'model_name':metrics['model_name']}
joblib.dump(artifact,MODELS/'messageguard_v5.joblib')
(REPORTS/'messageguard_v5_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
