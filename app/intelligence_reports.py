"""Shared ML intelligence and explainability for SentryMesh.

This layer keeps model inference separate from presentation.  It deliberately
reports what the models observed, what evidence contributed, what was unknown,
and what action is appropriate.  It does not convert heuristics into a hidden
risk score.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import re, math, json, joblib
import numpy as np

BASE=Path(__file__).resolve().parent.parent
MODELS=BASE/'models'

class MessageGuardModel:
    def __init__(self):
        self.artifact=None
        p=MODELS/'messageguard_v5.joblib'
        if p.exists():
            self.artifact=joblib.load(p)
    @property
    def available(self): return self.artifact is not None
    def analyze(self,text:str)->Dict[str,Any]:
        if not self.artifact: raise RuntimeError('MessageGuard v5 artifact unavailable')
        w=self.artifact['word_vectorizer']; c=self.artifact['char_vectorizer']; clf=self.artifact['model']
        Xw=w.transform([text]); Xc=c.transform([text]); X=np.hstack([Xw.toarray(),Xc.toarray()])
        p=float(clf.predict_proba(X)[0][list(clf.classes_).index('suspicious')])
        # Exact linear contribution for active word/char features.
        coef=clf.coef_[0]
        if list(clf.classes_)[1]=='suspicious': pass
        else: coef=-coef
        aw=X[0]
        names=list(w.get_feature_names_out())+list(c.get_feature_names_out())
        contrib=aw*coef
        pos=sorted([(names[i],float(contrib[i])) for i in np.flatnonzero(aw) if contrib[i]>0],key=lambda x:x[1],reverse=True)[:8]
        neg=sorted([(names[i],float(contrib[i])) for i in np.flatnonzero(aw) if contrib[i]<0],key=lambda x:x[1])[:8]
        threshold=float(self.artifact['threshold'])
        return {'probability':round(p,4),'threshold':round(threshold,4),'decision':'suspicious' if p>=threshold else 'legitimate','positive_evidence':[{'feature':a,'contribution':round(b,5)} for a,b in pos],'negative_evidence':[{'feature':a,'contribution':round(b,5)} for a,b in neg],'model_name':self.artifact['model_name'],'model_type':'word+character TF-IDF SGD logistic-loss classifier'}

class ParentGuardianModel:
    def __init__(self):
        p=MODELS/'parentguardian_safety_v1.joblib'; self.artifact=joblib.load(p) if p.exists() else None
    @property
    def available(self): return self.artifact is not None
    def analyze(self,text:str):
        if not self.artifact: raise RuntimeError('ParentGuardian model unavailable')
        w=self.artifact['word_vectorizer']; c=self.artifact['char_vectorizer']; model=self.artifact['model']
        Xw=w.transform([text]); Xc=c.transform([text]); X=np.hstack([Xw.toarray(),Xc.toarray()])
        probs=model.predict_proba(X)[0]
        classes=list(model.classes_)
        order=np.argsort(probs)[::-1]
        top=[{'category':str(classes[i]),'probability':round(float(probs[i]),4)} for i in order[:5]]
        # Per-class linear attribution for top class.
        top_i=int(order[0]); est=model.estimators_[top_i]; coef=est.coef_[0]
        names=list(w.get_feature_names_out())+list(c.get_feature_names_out()); vec=X[0]; contrib=vec*coef
        pos=sorted([(names[i],float(contrib[i])) for i in np.flatnonzero(vec) if contrib[i]>0],key=lambda x:x[1],reverse=True)[:8]
        neg=sorted([(names[i],float(contrib[i])) for i in np.flatnonzero(vec) if contrib[i]<0],key=lambda x:x[1])[:8]
        return {'top_categories':top,'primary_category':str(classes[top_i]),'primary_probability':round(float(probs[top_i]),4),'positive_evidence':[{'feature':a,'contribution':round(b,5)} for a,b in pos],'negative_evidence':[{'feature':a,'contribution':round(b,5)} for a,b in neg],'model_name':self.artifact['model_name'],'model_note':'Safety-domain classifier; output describes communication patterns, not a diagnosis of abuse, grooming, intent, or criminality.'}

messageguard=MessageGuardModel(); parentguardian=ParentGuardianModel()

def entropy(values):
    vals=[float(v) for v in values if v>0]; return round(-sum(v*math.log(v,2) for v in vals),4) if vals else 0.0

def extract_basic_entities(text):
    urls=re.findall(r'https?://[^\s<>]+',text,flags=re.I)
    emails=re.findall(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',text)
    phones=re.findall(r'(?<!\w)(?:\+?91[ -]?)?[6-9]\d{9}(?!\w)',text)
    upi=re.findall(r'\b[\w.-]{2,}@[\w.-]{2,}\b',text)
    amounts=re.findall(r'(?:₹|rs\.?|inr)\s?[\d,]+(?:\.\d+)?',text,flags=re.I)
    return {'urls':urls,'emails':emails,'phone_numbers':phones,'upi_ids':[u for u in upi if u not in emails],'amounts':amounts}

def build_message_report(text,channel):
    r=messageguard.analyze(text)
    ent=extract_basic_entities(text)
    tactics=[]
    # Tactic model is optional but real learned output when artifact exists.
    tp=MODELS/'tactic_v2.joblib'
    if tp.exists():
        a=joblib.load(tp); w=a['word_vectorizer']; c=a['char_vectorizer']; m=a['model']; X=np.hstack([w.transform([text]).toarray(),c.transform([text]).toarray()]); probs=m.predict_proba(X)
        for i,t in enumerate(a['tactics']):
            tactics.append({'tactic':t,'probability':round(float(probs[i][0][1]),4)})
        tactics.sort(key=lambda x:x['probability'],reverse=True)
    top_t=[x for x in tactics if x['probability']>=.5][:5]
    p=r['probability']; t=r['threshold']
    margin=round(p-t,4)
    uncertainty='low' if abs(margin)>=.25 else ('medium' if abs(margin)>=.10 else 'high')
    reasons=[]
    if r['positive_evidence']: reasons.append('The trained classifier increased suspicion most through the listed text features; these are model contributions, not manually assigned weights.')
    if r['negative_evidence']: reasons.append('The classifier also found features that pull toward a legitimate interpretation; these counter-signals are shown rather than hidden.')
    if top_t: reasons.append('A separately trained multi-label tactic model identified the following communication patterns with the probabilities shown.')
    if ent['urls']: reasons.append(f"The message contains {len(ent['urls'])} URL(s); URL safety should be checked separately by WebGuard rather than assumed from text alone.")
    if ent['amounts'] or ent['upi_ids']: reasons.append('Financial entities were extracted and should be independently verified before any transfer or approval.')
    return {'module':'MessageGuard','channel':channel,'decision':r['decision'],'risk_score':round(p,4),'threshold':t,'decision_margin':margin,'uncertainty':uncertainty,'model':r['model_name'],'model_type':r['model_type'],'model_evidence':{'suspicious':r['positive_evidence'],'legitimate':r['negative_evidence']},'tactics':top_t,'entities':ent,'explanation':reasons,'limitations':['Text-only inference cannot authenticate the sender.','A low score does not prove safety; a high score does not prove malicious intent.'],'recommended_actions':['Pause before transferring money or sharing credentials.','Verify unexpected requests using a trusted, independently obtained contact channel.','Never disclose OTPs, UPI PINs, passwords or remote-control codes.'],'channel_handling':f'Analyzed as {channel}; channel changes the explanation/actions but the underlying classifier is shared.'}

def build_parent_report(text,channel):
    p=parentguardian.analyze(text); probs=[x['probability'] for x in p['top_categories']]
    primary=p['primary_probability']; category=p['primary_category']
    score=(1.0-primary if category=='benign' else primary)
    # Financial/remote social-engineering overlap is useful as a secondary model, not a rule.
    secondary=None
    try: secondary=messageguard.analyze(text)
    except Exception: pass
    if secondary and secondary['probability']>score and category=='benign':
        score=secondary['probability']; category='financial_or_cyber_safety_overlap'
    risk=('low_signal' if category=='benign' and score>=0.50 else ('high' if category!='benign' and score>=.75 else ('elevated' if category!='benign' and score>=.45 else ('uncertain' if category!='benign' and score>=.30 else 'low_signal'))))
    actions={
      'threat':['If you believe there is immediate danger, move to a safer place and contact a trusted adult or appropriate emergency/support service. Preserve the original message.'],
      'coercion_blackmail':['Do not pay or comply under pressure. Preserve the message/screenshots and involve a trusted adult or appropriate platform/support channel.'],
      'secrecy_isolation':['Consider whether the request is pressuring you to avoid trusted people. Preserve the conversation and consider telling a trusted adult.'],
      'unsafe_image_request':['Do not send private images. Preserve the request and tell a trusted adult or use the platform reporting tools if appropriate.'],
      'location_meetup_risk':['Do not share live location or meet an unknown/contacted person alone. Involve a trusted adult.'],
      'harassment':['Preserve the messages, use platform block/report controls if appropriate, and involve a trusted person if the behavior continues or feels unsafe.'],
      'grooming_risk_pattern':['The model detected a communication pattern associated with secrecy/age-inappropriate pressure. This is not a finding that grooming occurred; preserve context and involve a trusted adult.'],
      'financial_scam':['Do not send money or approve payment requests until independently verified.'],
      'remote_access_social_engineering':['Do not install remote-control software or share screen/access codes because of an unsolicited request.'],
      'benign':['No strong safety-domain pattern was detected by the ParentGuardian model; continue normal caution.']}
    return {'module':'ParentGuardian','channel':channel,'decision':risk,'risk_score':round(score,4),'primary_category':category,'model':p['model_name'],'model_evidence':{'top_categories':p['top_categories'],'supporting_features':p['positive_evidence'],'counter_features':p['negative_evidence']},'secondary_fraud_model':secondary,'explanation':['The primary score comes from a supervised safety-domain text model trained on SentryMesh reviewed examples plus explicitly labeled synthetic augmentation.','The category describes an observable communication pattern; it does not diagnose abuse, grooming, criminality, or intent.'],'recommended_actions':actions.get(category,actions['benign']),'uncertainty':'high' if .35<score<.75 else 'medium' if score<.9 else 'low','privacy':['Analyze only text explicitly submitted by an authorized user.','No covert monitoring or background scraping is performed.']}
