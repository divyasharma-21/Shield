"""AppGuard: metadata discovery + transparent application-risk analysis."""
import json,re
from pathlib import Path
from typing import Any,Dict,List,Optional

BASE=Path(__file__).resolve().parent.parent
PROJECT_ROOT=Path(__file__).resolve().parents[2]
CATALOG_PATH=BASE/'data'/'app_catalog.json'
if not CATALOG_PATH.exists():
    CATALOG_PATH=PROJECT_ROOT/'data'/'app_catalog.json'
REMOTE_ACCESS={'remote_access','screen_control'}
TRUSTED={'google play','play store','apple app store','app store','microsoft store'}
UNTRUSTED={'unknown','sideloaded','apk','direct apk','third-party store','unknown source'}

def norm(v): return re.sub(r'\s+',' ',str(v or '').strip().lower())
def catalog():
    try:return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))
    except Exception:return {}

def discover_app(app_name):
    q=norm(app_name); c=catalog()
    exact=[]
    for item in c.values():
        if q==norm(item['app_name']) or q in {norm(x) for x in item.get('aliases',[])}: exact.append(item)
    if exact: return {'status':'catalog_match','source':'SentryMesh curated app metadata catalog','metadata':exact[0]}
    # fuzzy token containment, still explicit about confidence
    for item in c.values():
        aliases=[norm(item['app_name'])]+[norm(x) for x in item.get('aliases',[])]
        if any(q and (q in a or a in q) for a in aliases): return {'status':'catalog_match','source':'SentryMesh curated app metadata catalog','metadata':item,'match_note':'Name matched an alias; verify package/publisher before trusting the result.'}
    return {'status':'not_found','source':'local catalog only','metadata':None,'match_note':'No verified metadata is available for this app name. The system does not invent package, publisher, permissions, or reputation.'}

def analyze_app(app_name,package_name=None,publisher=None,installation_source=None,permissions=None,accessibility_enabled=False,screen_capture_enabled=False,overlay_enabled=False,sms_access_enabled=False,contacts_access_enabled=False,device_admin_enabled=False,reputation=None):
    discovery=discover_app(app_name)
    meta=discovery.get('metadata') or {}
    # User-supplied fields override discovered values.
    package_name=package_name or meta.get('package_name'); publisher=publisher or meta.get('publisher'); installation_source=installation_source or meta.get('installation_source')
    capabilities=set(meta.get('capabilities',[]))
    permissions=set(norm(x) for x in (permissions or []))
    signals=[]; drivers=[]; score=0.0
    source=norm(installation_source)
    if source in UNTRUSTED: score+=.20; drivers.append(('untrusted_installation_source',.20,'The supplied installation source is sideloaded or third-party.'))
    elif source in TRUSTED: signals.append('Installation source is reported as a known official application store.')
    if 'remote_access' in capabilities: score+=.20; drivers.append(('remote_access_capability',.20,'The discovered app is designed to provide remote device access. This is not inherently malicious, but it becomes high-risk when access is unsolicited or coerced.'))
    if 'screen_control' in capabilities: score+=.10; drivers.append(('screen_control',.10,'The app can support remote viewing/control workflows.'))
    if accessibility_enabled or any('accessibility' in p for p in permissions): score+=.15; drivers.append(('accessibility',.15,'Accessibility-service access can enable broad interaction with on-screen content.'))
    if screen_capture_enabled or any(x in permissions for x in ['screen_capture','screen_recording','media_projection']): score+=.15; drivers.append(('screen_capture',.15,'Screen capture/recording can expose sensitive on-screen information.'))
    if overlay_enabled or any('overlay' in p or 'draw_over' in p for p in permissions): score+=.10; drivers.append(('overlay',.10,'Overlay capability can place UI above other applications and may increase phishing/social-engineering risk.'))
    if sms_access_enabled or any(x in permissions for x in ['sms','read_sms','send_sms']): score+=.10; drivers.append(('sms_access',.10,'SMS access can expose authentication messages.'))
    if contacts_access_enabled or any('contact' in p for p in permissions): score+=.05; drivers.append(('contacts_access',.05,'Contacts access exposes address-book information.'))
    if device_admin_enabled or any('device_admin' in p for p in permissions): score+=.15; drivers.append(('device_admin',.15,'Device-administrator capability can provide powerful device controls.'))
    if reputation:
        if reputation.get('known_malicious') is True: score+=.40; drivers.append(('reputation_malicious',.40,'Supplied reputation evidence marks the app as known malicious.'))
        elif reputation.get('suspicious') is True: score+=.20; drivers.append(('reputation_suspicious',.20,'Supplied reputation evidence marks the app as suspicious.'))
    score=min(score,1.0)
    if discovery['status']=='not_found' and not any([package_name,publisher,permissions,accessibility_enabled,screen_capture_enabled,overlay_enabled,sms_access_enabled,contacts_access_enabled,device_admin_enabled,reputation]):
        return {
            'app_name': app_name, 'package_name': package_name, 'publisher': publisher,
            'installation_source': installation_source, 'status': 'unverified',
            'risk_level': 'unverified', 'risk_score': None, 'signals': [
                'No verified application metadata matched the supplied app name.'
            ],
            'evidence': {
                'discovery': discovery,
                'identity': {
                    'app_name_supplied': bool(app_name),
                    'package_verified': False,
                    'publisher_verified': False,
                    'installation_source_verified': False,
                    'reputation_available': bool(reputation),
                },
                'risk_drivers': [], 'capabilities': [], 'permissions': []
            },
            'explainable_report': {
                'summary': 'SentryMesh could not establish a verifiable identity for this application, so it does not assign a low-risk score.',
                'score_method': 'No risk probability is produced when application identity cannot be verified from available evidence.',
                'evidence_items': [
                    {'label':'App identity','contribution':None,'reason':'The supplied app name did not match the curated verified metadata catalog.','source':'identity verification'},
                    {'label':'Package identifier','contribution':None,'reason':'No package/bundle identifier was supplied or verified.','source':'input metadata'},
                    {'label':'Publisher','contribution':None,'reason':'No publisher was supplied or verified.','source':'input metadata'},
                    {'label':'Installation provenance','contribution':None,'reason':'Installation source alone cannot establish that this specific app identity is authentic.','source':'provenance'},
                    {'label':'Observed capabilities','contribution':None,'reason':'No sensitive capabilities were supplied for this unverified app.','source':'device context'},
                ],
                'why_no_score': [
                    'The app identity is not verified from the available metadata.',
                    'A missing catalog match is not evidence that the app is malicious.',
                    'A numeric risk score would imply evidence that SentryMesh does not actually have.'
                ]
            },
            'recommended_actions': [
                'Verify the exact package name and publisher in the official app store before installing.',
                'Do not grant accessibility, screen capture, overlay or remote-control access because of an unsolicited request.',
            ],
            'note': 'Unverified application identity; no fabricated risk score.'
        }
    level='high' if score>=.70 else 'elevated' if score>=.45 else 'low'
    summary=f'{level.upper()} risk based on {len(drivers)} observed risk driver(s). Risk drivers are evidence signals, not a verdict that the application is malicious.'
    return {'app_name':meta.get('app_name',app_name),'package_name':package_name,'publisher':publisher,'installation_source':installation_source,'status':'analyzed','risk_level':level,'risk_score':round(score,4),'signals':signals+[x[2] for x in drivers],'evidence':{'discovery':discovery,'risk_drivers':[{'signal':a,'contribution':b,'reason':c} for a,b,c in drivers],'capabilities':sorted(capabilities),'permissions':sorted(permissions),'catalog_risk_notes':meta.get('risk_notes',[])},'explainable_report':{'summary':summary,'score_method':'Transparent evidence aggregation over discovered metadata and explicitly supplied permissions/capabilities. No hidden app-name keyword score is used.','drivers':[{'signal':a,'contribution':round(b,4),'reason':c} for a,b,c in drivers],'evidence_items':([{'label':a.replace('_',' ').title(),'contribution':round(b,4),'reason':c,'source':'observed app metadata / supplied device context'} for a,b,c in drivers] or [
        {'label':'Verified app identity','contribution':0.0,'reason':'The app name matched a known entry in the curated SentryMesh metadata catalog.','source':'identity catalog'},
        {'label':'No observed sensitive capability','contribution':0.0,'reason':'No accessibility, screen capture, overlay, SMS, contacts or device-admin capability was supplied as enabled.','source':'device context'},
        {'label':'No supplied malicious reputation','contribution':0.0,'reason':'No external malicious-reputation signal was supplied for this assessment.','source':'reputation input'}
    ]),'counter_signals':['Official-store metadata is a provenance signal, not proof that an app is harmless.']},'recommended_actions':(['Do not grant remote-control or screen-sharing access to an unsolicited caller.'] if 'remote_access' in capabilities else [])+['Review sensitive permissions and whether they are necessary for the app purpose.','Verify the publisher/package before installing a similarly named app.'],'note':'AppGuard does not uninstall, block, monitor, or control applications automatically.'}
