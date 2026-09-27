
import { useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import './index.css';

import {
  BrowserRouter,
  Link,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router-dom';

import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  FileCheck2,
  FileWarning,
  Flag,
  Globe2,
  Info,
  KeyRound,
  Lock,
  Menu,
  MessageSquare,
  Mic,
  Network,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Square,
  Target,
  UploadCloud,
  Users,
  X,
} from 'lucide-react';

import { PrivacyPage } from './pages/PrivacyPage';
import { ResponsePage } from './pages/ResponsePage';


// ============================================================
// API
// ============================================================

const API =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000';


// ============================================================
// TYPES
// ============================================================

type ModuleKey =
  | 'message'
  | 'web'
  | 'app'
  | 'parent'
  | 'report'
  | 'ops';

type ModuleMeta = {
  key: ModuleKey;
  label: string;
  short: string;
  description: string;
  icon: typeof Shield;
  accent: string;
};


// ============================================================
// MODULE REGISTRY
// ============================================================

const MODULES: ModuleMeta[] = [
  {
    key: 'message',
    label: 'MessageGuard',
    short: 'MSG',
    description:
      'Inspect suspicious messages, payment requests and social-engineering tactics.',
    icon: MessageSquare,
    accent: 'cyan',
  },
  {
    key: 'web',
    label: 'WebGuard',
    short: 'WEB',
    description:
      'Inspect URLs, domains, redirects and deceptive-site indicators.',
    icon: Globe2,
    accent: 'sky',
  },
  {
    key: 'app',
    label: 'AppGuard',
    short: 'APP',
    description:
      'Understand app provenance, permissions and remote-control capabilities.',
    icon: Smartphone,
    accent: 'violet',
  },
  {
    key: 'parent',
    label: 'ParentGuardian',
    short: 'FAM',
    description:
      'Review family-safety signals with transparent, consent-based analysis.',
    icon: Users,
    accent: 'emerald',
  },
  {
    key: 'report',
    label: 'ReportGuard',
    short: 'RPT',
    description:
      'Sanitize and quarantine suspicious-activity reports for review.',
    icon: Flag,
    accent: 'amber',
  },
  {
    key: 'ops',
    label: 'Model Ops',
    short: 'OPS',
    description:
      'Inspect active models, evaluation artifacts and platform health.',
    icon: Activity,
    accent: 'indigo',
  },
];


// ============================================================
// ROUTE HELPERS
// ============================================================

function moduleMeta(key?: string): ModuleMeta {
  return (
    MODULES.find(module => module.key === key) ||
    MODULES[0]
  );
}


// ============================================================
// API HELPERS
// ============================================================

async function post(path: string, body: unknown) {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(
      typeof data?.detail === 'string'
        ? data.detail
        : data?.message ||
        `Request failed (${res.status})`,
    );
  }

  return data;
}


async function get(path: string) {
  const res = await fetch(`${API}${path}`, {
    headers: {
      Accept: 'application/json',
    },
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(
      typeof data?.detail === 'string'
        ? data.detail
        : `Request failed (${res.status})`,
    );
  }

  return data;
}


// ============================================================
// APP SHELL
// ============================================================

function AppShell({
  children,
}: {
  children: ReactNode;
}) {
  const location = useLocation();

  const [open, setOpen] = useState(false);

  const activeKey =
    location.pathname.split('/')[1] || '';

  const activeModule = moduleMeta(activeKey);

  return (
    <div className="app-shell">

      {/* SIDEBAR */}
      <aside
        className={`sidebar ${open ? 'open' : ''
          }`}
      >

        <div className="brand">

          <div className="brand-mark">
            <Shield size={20} />
          </div>

          <div>
            <strong>SENTRYMESH</strong>
            <span>SECURITY INTELLIGENCE</span>
          </div>

          <button
            className="mobile-close"
            onClick={() => setOpen(false)}
            aria-label="Close menu"
          >
            <X size={18} />
          </button>

        </div>


        <nav className="module-nav">

          {/* COMMAND CENTER */}
          <Link
            to="/"
            onClick={() => setOpen(false)}
            className={
              location.pathname === '/'
                ? 'active'
                : ''
            }
          >
            <Target size={16} />
            <span>Command Center</span>
          </Link>


          <div className="nav-section-label">
            INTELLIGENCE MODULES
          </div>


          {/* MODULE ROUTES */}
          {MODULES.map(module => {
            const Icon = module.icon;

            return (
              <Link
                key={module.key}
                to={`/${module.key}`}
                onClick={() => setOpen(false)}
                className={
                  activeKey === module.key
                    ? 'active'
                    : ''
                }
              >
                <Icon size={16} />
                <span>{module.label}</span>
                <ChevronRight size={13} />
              </Link>
            );
          })}


          <div className="nav-section-label">
            PLATFORM
          </div>


          {/* PRIVACY */}
          <Link
            to="/privacy"
            onClick={() => setOpen(false)}
            className={
              location.pathname === '/privacy'
                ? 'active'
                : ''
            }
          >
            <Lock size={16} />
            <span>Privacy & Safety</span>
          </Link>


          {/* RESPONSE */}
          <Link
            to="/response"
            onClick={() => setOpen(false)}
            className={
              location.pathname === '/response'
                ? 'active'
                : ''
            }
          >
            <ArrowRight size={16} />
            <span>Response Center</span>
          </Link>

        </nav>


        <div className="sidebar-footer">

          <div className="system-status">
            <span className="status-dot" />
            <span>INTELLIGENCE CORE ONLINE</span>
          </div>

          <small>
            Evidence-first cybersecurity analysis
          </small>

        </div>

      </aside>


      {/* MOBILE OVERLAY */}
      {open && (
        <button
          className="sidebar-overlay"
          onClick={() => setOpen(false)}
          aria-label="Close navigation"
        />
      )}


      {/* MAIN */}
      <main className="main-content">

        <header className="topbar">

          <button
            className="mobile-menu"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>


          <div className="topbar-context">
            <span>SENTRYMESH</span>
            <ChevronRight size={13} />
            <b>{activeModule.label}</b>
          </div>


          <div className="topbar-right">

            <div className="live-indicator">
              <span className="status-dot" />
              LIVE
            </div>

          </div>

        </header>


        <div className="page-container">
          {children}
        </div>

      </main>

    </div>
  );
}


// ============================================================
// HOME
// ============================================================

function Home() {
  return (
    <>

      <div className="hero">

        <div className="hero-copy">

          <div className="eyebrow">
            <span className="status-dot" />
            SHARED CYBERSECURITY INTELLIGENCE CORE
          </div>


          <h1>
            One intelligence layer.
            <br />
            <span>Multiple digital threats.</span>
          </h1>


          <p>
            SentryMesh connects message, web,
            application and family-safety analysis
            through one evidence-first intelligence
            pipeline.
          </p>


          <div className="hero-actions">

            <Link
              to="/message"
              className="primary-button"
            >
              Analyze a threat
              <ArrowRight size={15} />
            </Link>


            <Link
              to="/privacy"
              className="secondary-button"
            >
              <Lock size={14} />
              Privacy model
            </Link>

          </div>

        </div>


        <div className="hero-core">

          <div className="core-ring outer" />
          <div className="core-ring middle" />


          <div className="core-center">
            <Shield size={30} />
            <b>CORE</b>
            <span>ONLINE</span>
          </div>


          <div className="core-node node-one">
            <MessageSquare size={15} />
            MSG
          </div>


          <div className="core-node node-two">
            <Globe2 size={15} />
            WEB
          </div>


          <div className="core-node node-three">
            <Smartphone size={15} />
            APP
          </div>


          <div className="core-node node-four">
            <Users size={15} />
            FAM
          </div>

        </div>

      </div>


      <section className="module-grid">

        {MODULES.map(module => {

          const Icon = module.icon;

          return (
            <Link
              to={`/${module.key}`}
              key={module.key}
              className={`module-card accent-${module.accent}`}
            >

              <div className="module-card-top">

                <div className="module-icon">
                  <Icon size={19} />
                </div>

                <span>{module.short}</span>

              </div>


              <h3>{module.label}</h3>

              <p>{module.description}</p>


              <div className="module-card-action">
                Open module
                <ArrowRight size={14} />
              </div>

            </Link>
          );

        })}

      </section>


      <section className="platform-strip">

        <div>
          <ShieldCheck size={17} />
          <span>Evidence-based</span>
        </div>

        <div>
          <Lock size={17} />
          <span>Privacy-conscious</span>
        </div>

        <div>
          <ClipboardCheck size={17} />
          <span>Explainable</span>
        </div>

        <div>
          <Network size={17} />
          <span>Shared intelligence</span>
        </div>

      </section>

    </>
  );
}


// ============================================================
// PAGE HEADER
// ============================================================

function PageHeader({
  meta,
  eyebrow,
}: {
  meta: ModuleMeta;
  eyebrow?: string;
}) {

  const Icon = meta.icon;

  return (
    <div className="page-header">

      <div>

        <div className="eyebrow">
          {eyebrow ||
            `SENTRYMESH / ${meta.short}`}
        </div>


        <div className="page-title-row">

          <div
            className={`page-title-icon accent-${meta.accent}`}
          >
            <Icon size={21} />
          </div>


          <div>

            <h1>{meta.label}</h1>

            <p>{meta.description}</p>

          </div>

        </div>

      </div>

    </div>
  );
}


// ============================================================
// PANEL
// ============================================================

function Panel({
  title,
  kicker,
  icon: Icon,
  children,
  className = '',
}: {
  title: string;
  kicker?: string;
  icon?: typeof Shield;
  children: ReactNode;
  className?: string;
}) {

  return (
    <section className={`panel ${className}`}>

      <div className="panel-header">

        <div>

          {kicker && (
            <div className="panel-kicker">
              {kicker}
            </div>
          )}

          <h2>{title}</h2>

        </div>


        {Icon && (
          <div className="panel-icon">
            <Icon size={17} />
          </div>
        )}

      </div>


      <div className="panel-body">
        {children}
      </div>

    </section>
  );
}


// ============================================================
// ANALYZE BUTTON
// ============================================================

function AnalyzeButton({
  onClick,
  loading,
  label = 'Analyze',
}: {
  onClick: () => void;
  loading: boolean;
  label?: string;
}) {

  return (
    <button
      className="primary-button analyze-button"
      onClick={onClick}
      disabled={loading}
    >

      {loading ? (
        <>
          <RefreshCw
            size={15}
            className="spin"
          />
          Analyzing...
        </>
      ) : (
        <>
          <Search size={15} />
          {label}
        </>
      )}

    </button>
  );
}


// ============================================================
// ERROR BOX
// ============================================================

function ErrorBox({
  error,
}: {
  error: string;
}) {

  if (!error) return null;

  return (
    <div className="error-box">

      <AlertOctagon size={17} />

      <div>

        <b>Analysis unavailable</b>

        <span>{error}</span>

      </div>

    </div>
  );
}


// ============================================================
// RISK BADGE
// ============================================================

function RiskBadge({
  level,
  score,
}: {
  level: any;
  score: number | null;
}) {
  const displayLevel = String(
    level ?? 'unknown',
  )
    .split('_')
    .join(' ')
    .toUpperCase();

  const percentage =
    typeof score === 'number'
      ? score <= 1
        ? Math.round(score * 100)
        : Math.round(score)
      : null;

  const tone =
    displayLevel.includes('UNVERIFIED')
      ? 'neutral'
      : percentage !== null &&
        percentage >= 70
        ? 'danger'
        : percentage !== null &&
          percentage >= 40
          ? 'warning'
          : 'safe';

  return (
    <div className={`risk-badge ${tone}`}>
      <span className="risk-pulse" />

      <div>
        <small>ASSESSMENT</small>

        <strong>
          {displayLevel}
        </strong>
      </div>

      {percentage !== null && (
        <b>
          {percentage}%
        </b>
      )}
    </div>
  );
}


// ============================================================
// EVIDENCE ROW
// ============================================================

function EvidenceRow({
  index,
  title,
  reason,
}: {
  index: number;
  title: string;
  reason: string;
}) {

  return (
    <div className="evidence-row">

      <span className="evidence-index">
        {String(index).padStart(2, '0')}
      </span>


      <div>

        <b>{title}</b>

        <p>{reason}</p>

      </div>

    </div>
  );
}


// ============================================================
// EVIDENCE BUILDER
// ============================================================

function buildEvidenceRows(data: any) {
  if (!data) return [];

  const rows: any[] = [];

  /*
   * Convert any backend value into safe readable text.
   * This prevents [object Object] from appearing in the UI.
   */
  const stringifyValue = (value: any): string => {
    if (value == null) return '';

    if (typeof value === 'string') {
      return value;
    }

    if (
      typeof value === 'number' ||
      typeof value === 'boolean'
    ) {
      return String(value);
    }

    if (Array.isArray(value)) {
      return value
        .map((item) => stringifyValue(item))
        .filter(Boolean)
        .join(', ');
    }

    if (typeof value === 'object') {
      return Object.entries(value)
        .map(
          ([key, val]) =>
            `${key
              .split('_')
              .join(' ')}: ${stringifyValue(val)}`,
        )
        .join(' • ');
    }

    return String(value);
  };

  /*
   * Add one evidence row.
   */
  const addRow = (
    item: any,
    fallbackLabel: string,
    fallbackReason: string,
    source: string,
  ) => {
    if (item == null) return;

    /*
     * Plain string / number
     */
    if (
      typeof item === 'string' ||
      typeof item === 'number'
    ) {
      rows.push({
        title: stringifyValue(item),
        reason: fallbackReason,
        source,
        contribution: undefined,
      });

      return;
    }

    /*
     * Backend object
     */
    if (typeof item === 'object') {
      const rawLabel =
        item.label ??
        item.feature ??
        item.signal ??
        item.tactic ??
        item.category ??
        item.name ??
        item.type ??
        item.term ??
        fallbackLabel;

      const rawReason =
        item.reason ??
        item.explanation ??
        item.description ??
        item.message ??
        fallbackReason;

      const contribution =
        typeof item.contribution === 'number'
          ? item.contribution
          : typeof item.weight === 'number'
            ? item.weight
            : typeof item.probability === 'number'
              ? item.probability
              : undefined;

      rows.push({
        title: stringifyValue(rawLabel)
          .split('_')
          .join(' '),

        reason: stringifyValue(rawReason),

        source:
          typeof item.source === 'string'
            ? item.source
            : source,

        contribution,
      });
    }
  };

  /*
   * --------------------------------------------------
   * 1. EXPLAINABLE REPORT
   * --------------------------------------------------
   */

  const explanation =
    data.explainable_report || {};

  if (
    Array.isArray(
      explanation.evidence_items,
    )
  ) {
    explanation.evidence_items.forEach(
      (item: any) =>
        addRow(
          item,
          'Model evidence',
          'This evidence contributed to the assessment.',
          'Model evidence',
        ),
    );
  }

  /*
   * --------------------------------------------------
   * 2. MODEL DRIVERS
   * --------------------------------------------------
   */

  if (
    Array.isArray(
      explanation.drivers,
    )
  ) {
    explanation.drivers.forEach(
      (item: any) =>
        addRow(
          item,
          'Model signal',
          'This learned model signal contributed to the assessment.',
          'Trained classifier',
        ),
    );
  }

  /*
   * --------------------------------------------------
   * 3. SUSPICIOUS MODEL EVIDENCE
   * --------------------------------------------------
   */

  const modelEvidence =
    data.model_evidence || {};

  if (
    Array.isArray(
      modelEvidence.suspicious,
    )
  ) {
    modelEvidence.suspicious.forEach(
      (item: any) =>
        addRow(
          item,
          'Suspicious model feature',
          'This learned feature increased the model score toward the suspicious interpretation.',
          'Trained MessageGuard classifier',
        ),
    );
  }

  if (
    Array.isArray(
      modelEvidence.signals_favoring_suspicious,
    )
  ) {
    modelEvidence
      .signals_favoring_suspicious
      .forEach(
        (item: any) =>
          addRow(
            item,
            'Suspicious model feature',
            'This learned feature increased suspicion.',
            'Trained MessageGuard classifier',
          ),
      );
  }

  /*
   * --------------------------------------------------
   * 4. COUNTER EVIDENCE
   * --------------------------------------------------
   */

  if (
    Array.isArray(
      modelEvidence.legitimate,
    )
  ) {
    modelEvidence.legitimate.forEach(
      (item: any) =>
        addRow(
          item,
          'Counter-signal',
          'This learned feature pulled the model toward a legitimate interpretation.',
          'Trained MessageGuard classifier',
        ),
    );
  }

  if (
    Array.isArray(
      modelEvidence.signals_favoring_legitimate,
    )
  ) {
    modelEvidence
      .signals_favoring_legitimate
      .forEach(
        (item: any) =>
          addRow(
            item,
            'Counter-signal',
            'This learned feature pulled the model toward a legitimate interpretation.',
            'Trained MessageGuard classifier',
          ),
      );
  }

  /*
   * --------------------------------------------------
   * 5. TACTIC EVIDENCE
   * --------------------------------------------------
   */

  if (Array.isArray(data.tactics)) {
    data.tactics
      .filter(
        (item: any) =>
          Number(
            item?.probability ?? 0,
          ) >= 0.5,
      )
      .forEach(
        (item: any) =>
          addRow(
            item,
            'Communication tactic',
            'A separately trained tactic model identified this communication pattern.',
            'Tactic classifier',
          ),
      );
  }

  /*
   * --------------------------------------------------
   * 6. EXTRACTED ENTITIES
   * --------------------------------------------------
   */

  const entities =
    data.entities || {};

  Object.entries(entities).forEach(
    ([key, value]: [
      string,
      any,
    ]) => {
      if (
        value == null ||
        value === false ||
        (Array.isArray(value) &&
          value.length === 0)
      ) {
        return;
      }

      const readableKey = key
        .split('_')
        .join(' ');

      rows.push({
        title: readableKey,

        reason:
          `The submitted message contained ${readableKey} information.`,

        source:
          'Entity extraction',

        contribution:
          undefined,
      });
    },
  );

  /*
   * --------------------------------------------------
   * 7. URL / WEBGUARD EVIDENCE
   * --------------------------------------------------
   */

  const evidence =
    data.evidence;

  if (evidence) {
    const addObservable = (
      title: string,
      value: any,
      reason: string,
      source = 'Observable evidence',
    ) => {
      if (
        value === undefined ||
        value === null ||
        value === false ||
        (Array.isArray(value) &&
          value.length === 0)
      ) {
        return;
      }

      rows.push({
        title,

        reason:
          `${reason} Observed: ${stringifyValue(value)}`,

        source,

        contribution:
          undefined,
      });
    };

    addObservable(
      'HTTPS',
      evidence.https,
      evidence.https
        ? 'The URL uses HTTPS transport; this does not by itself prove legitimacy.'
        : 'The URL does not use HTTPS.',
      'URL structure',
    );

    addObservable(
      'DNS resolution',
      evidence.dns?.resolved,
      evidence.dns?.resolved
        ? `Hostname resolved to ${evidence.dns
          ?.addresses?.length || 0
        } address(es).`
        : 'Hostname did not resolve at analysis time.',
      'DNS',
    );

    addObservable(
      'Brand impersonation',
      evidence.possible_brand_impersonation,
      'The hostname contains a known brand token without matching its known official domain.',
      'Domain identity',
    );

    addObservable(
      'Suspicious TLD',
      evidence.suspicious_tld,
      `The hostname uses ${evidence.suspicious_tld}, which warrants additional scrutiny.`,
      'Domain identity',
    );

    addObservable(
      'Suspicious URL terms',
      evidence.suspicious_terms,
      'The URL contains contextual security-related terms.',
      'URL path/query',
    );
  }

  return rows;
}


// ============================================================
// REPORT VIEW
// ============================================================

function ReportView({
  data,
  title = 'Analysis result',
}: {
  data: any;
  title?: string;
}) {
  const evidenceRows =
    buildEvidenceRows(data);

  /*
   * --------------------------------------------------
   * DECISION / RISK LEVEL
   * --------------------------------------------------
   */

  const level =
    data?.decision ||
    data?.risk_level ||
    data?.risk?.level ||
    data?.assessment?.risk_level ||
    data?.predicted_label ||
    data?.safety_level ||
    'unknown';

  /*
   * --------------------------------------------------
   * RISK SCORE
   * --------------------------------------------------
   */

  const rawScore =
    data?.risk_score ??
    data?.risk?.score ??
    data?.assessment?.risk_score ??
    data?.suspicious_probability ??
    data?.probability ??
    null;

  const score =
    typeof rawScore === 'number'
      ? rawScore > 1
        ? rawScore / 100
        : rawScore
      : null;

  /*
   * --------------------------------------------------
   * WEBGUARD DETECTION
   * --------------------------------------------------
   */

  const isWebGuard =
    !!data?.url ||
    !!data?.normalized_url ||
    !!data?.evidence?.ml_model;

  const fullMlAvailable =
    data?.evidence?.ml_model
      ?.available;

  const scoreLabel =
    isWebGuard &&
      fullMlAvailable === false
      ? 'URL-derived risk score'
      : 'Risk score';

  /*
   * --------------------------------------------------
   * SUMMARY
   * --------------------------------------------------
   */

  const summary =
    data?.summary ||
    data?.explanation ||
    data?.assessment?.summary ||
    data?.explainable_report?.summary ||
    'The analysis completed. Review the evidence below before taking action.';

  /*
   * --------------------------------------------------
   * RECOMMENDATIONS
   * --------------------------------------------------
   */

  const recommendations =
    data?.recommendations ||
    data?.recommended_actions ||
    data?.assessment?.recommendations ||
    [];

  return (
    <section className="result-stack">

      {/* --------------------------------------------- */}
      {/* RESULT HEADER */}
      {/* --------------------------------------------- */}

      <div className="result-header">

        <div>

          <div className="panel-kicker">
            ANALYSIS COMPLETE
          </div>

          <h2>
            {title}
          </h2>

          <p>
            {summary}
          </p>

        </div>

        <RiskBadge
          level={level}
          score={score}
        />

      </div>


      {/* --------------------------------------------- */}
      {/* EVIDENCE + ASSESSMENT */}
      {/* --------------------------------------------- */}

      <div className="result-grid">

        {/* EVIDENCE MAP */}

        <Panel
          title="Evidence map"
          kicker="WHY THIS ASSESSMENT WAS GIVEN"
          icon={ShieldAlert}
        >

          {evidenceRows.length > 0 ? (

            <div className="evidence-list">

              {evidenceRows.map(
                (
                  row: any,
                  index: number,
                ) => (

                  <EvidenceRow
                    key={`${row.title || 'evidence'}-${index}`}
                    index={index + 1}
                    title={
                      row.title ||
                      'Model evidence'
                    }
                    reason={
                      row.reason ||
                      'Evidence contributed to the assessment.'
                    }
                  />

                ),
              )}

            </div>

          ) : (

            <div className="muted-box">
              No structured evidence items
              were returned by the backend.
            </div>

          )}

        </Panel>


        {/* ASSESSMENT */}

        <Panel
          title="Assessment"
          kicker="CONFIDENCE & MODEL STATUS"
          icon={Activity}
        >

          <div className="assessment-metrics">

            {/* RISK SCORE */}

            <div className="metric-card">

              <small>
                {scoreLabel}
              </small>

              <strong>

                {score !== null
                  ? `${Math.round(
                    score * 100,
                  )}%`
                  : '—'}

              </strong>

            </div>


            {/* DECISION */}

            <div className="metric-card">

              <small>
                Decision
              </small>

              <strong>

                {String(
                  level,
                )
                  .split('_')
                  .join(' ')
                  .toUpperCase()}

              </strong>

            </div>


            {/* UNCERTAINTY */}

            <div className="metric-card">

              <small>
                Uncertainty
              </small>

              <strong>

                {data?.uncertainty !==
                  undefined

                  ? typeof data.uncertainty ===
                    'number'

                    ? `${Math.round(
                      data.uncertainty *
                      100,
                    )}%`

                    : String(
                      data.uncertainty,
                    )

                  : '—'}

              </strong>

            </div>


            {/* MODEL */}

            <div className="metric-card">

              <small>
                Model
              </small>

              <strong>

                {data?.model ||
                  data?.model_name ||
                  data?.classifier ||
                  'MessageGuard'}

              </strong>

            </div>

          </div>


          {/* THRESHOLD */}

          {data?.threshold !==
            undefined && (

              <div className="model-status-box">

                <div>

                  <small>
                    DECISION THRESHOLD
                  </small>

                  <b>

                    {typeof data.threshold ===
                      'number'

                      ? data.threshold.toFixed(
                        3,
                      )

                      : String(
                        data.threshold,
                      )}

                  </b>

                </div>

                <p>
                  The classifier decision is
                  interpreted relative to this
                  configured threshold.
                </p>

              </div>

            )}


          {/* DECISION MARGIN */}

          {data?.decision_margin !==
            undefined && (

              <div className="model-status-box">

                <div>

                  <small>
                    DECISION MARGIN
                  </small>

                  <b>

                    {typeof data.decision_margin ===
                      'number'

                      ? data.decision_margin.toFixed(
                        4,
                      )

                      : String(
                        data.decision_margin,
                      )}

                  </b>

                </div>

                <p>
                  Margin reported by the trained
                  classifier for this prediction.
                </p>

              </div>

            )}


          {/* WEBGUARD MODEL STATUS */}

          {isWebGuard && (

            <div className="model-status-box">

              <div>

                <small>
                  FULL WEB ML
                </small>

                <b>

                  {fullMlAvailable ===
                    true
                    ? 'EVALUATED'
                    : 'NOT EVALUATED'}

                </b>

              </div>

              <p>

                {data?.evidence
                  ?.ml_model
                  ?.reason ||
                  'URL-observable evidence is shown separately from webpage-dependent model evidence.'}

              </p>

            </div>

          )}


          {/* UNCERTAINTY EXPLANATION */}

          {data?.uncertainty !==
            undefined && (

              <div className="uncertainty-box">

                <Info size={15} />

                <div>

                  <b>
                    Uncertainty
                  </b>

                  <span>

                    {typeof data.uncertainty ===
                      'number'

                      ? `${Math.round(
                        data.uncertainty *
                        100,
                      )}% uncertainty`

                      : String(
                        data.uncertainty,
                      )}

                  </span>

                </div>

              </div>

            )}

        </Panel>

      </div>


      {/* --------------------------------------------- */}
      {/* RECOMMENDATIONS + RAW EVIDENCE */}
      {/* --------------------------------------------- */}

      <div className="result-grid">

        {/* RECOMMENDATIONS */}

        <Panel
          title="Recommended next steps"
          kicker="RESPONSE GUIDANCE"
          icon={ArrowRight}
        >

          {Array.isArray(
            recommendations,
          ) &&
            recommendations.length >
            0 ? (

            <div className="recommendation-list">

              {recommendations.map(
                (
                  item: any,
                  index: number,
                ) => (

                  <div
                    className="recommendation"
                    key={index}
                  >

                    <span>
                      {index + 1}
                    </span>

                    <p>

                      {typeof item ===
                        'string'

                        ? item

                        : item?.text ||
                        item?.action ||
                        item?.reason ||
                        JSON.stringify(
                          item,
                        )}

                    </p>

                  </div>

                ),
              )}

            </div>

          ) : (

            <div className="muted-box">
              No specific next-step
              recommendations were
              returned.
            </div>

          )}

        </Panel>


        {/* RAW STRUCTURED EVIDENCE */}

        <Panel
          title="Observable evidence"
          kicker="RAW STRUCTURED SIGNALS"
          icon={FileCheck2}
        >

          {data?.evidence ? (

            <pre className="structured-data">
              {JSON.stringify(
                data.evidence,
                null,
                2,
              )}
            </pre>

          ) : (

            <div className="muted-box">
              No additional structured
              evidence was returned.
            </div>

          )}

        </Panel>

      </div>


      {/* --------------------------------------------- */}
      {/* PRIVACY / SAFETY NOTICE */}
      {/* --------------------------------------------- */}

      <div className="privacy-notice">

        <Lock size={15} />

        <span>
          SentryMesh uses evidence-based
          analysis and should not be treated
          as proof of malicious intent.
          Review the underlying evidence
          before taking action.
        </span>

      </div>

    </section>
  );
}


// ============================================================
// MESSAGE GUARD
// ============================================================

function MessageGuard() {

  const meta =
    moduleMeta('message');


  const [text, setText] =
    useState('');

  const [channel, setChannel] =
    useState('sms');

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  const [result, setResult] =
    useState<any>(null);


  const examples = [
    {
      label: 'Bank phishing',
      text:
        'URGENT: Your SBI account will be blocked today. Verify your account immediately using https://sbi-login-security.xyz/verify-account and enter your OTP.',
    },

    {
      label: 'Prize scam',
      text:
        'Congratulations! You have won ₹50,000. Pay ₹999 processing fee through this UPI ID to receive your prize.',
    },

    {
      label: 'Benign',
      text:
        'Hi, I will reach home around 7 PM. Please keep dinner ready.',
    },
  ];


  const run = async () => {

    if (!text.trim()) {
      setError(
        'Please enter a message to analyze.',
      );
      return;
    }


    setLoading(true);
    setError('');
    setResult(null);


    try {

      const data = await post(
        '/analyze',
        {
          text,
          channel,
          user_consent: true,
        },
      );

      setResult(data);

    } catch (e: any) {

      setError(
        e.message ||
        'Message analysis failed.',
      );

    } finally {

      setLoading(false);

    }

  };


  return (
    <>

      <PageHeader
        meta={meta}
        eyebrow="MESSAGE INTELLIGENCE / SOCIAL ENGINEERING"
      />


      <div className="analyzer-layout">

        <Panel
          title="Inspect a message"
          kicker="INPUT"
          icon={MessageSquare}
        >

          <label className="field-label">

            Channel

            <select
              value={channel}
              onChange={e =>
                setChannel(
                  e.target.value,
                )
              }
            >

              <option value="sms">
                SMS
              </option>

              <option value="email">
                Email
              </option>

              <option value="whatsapp">
                WhatsApp
              </option>

              <option value="social_message">
                Social message
              </option>

              <option value="payment_message">
                Payment message
              </option>

            </select>

          </label>


          <label className="field-label">

            Message content

            <textarea
              className="analysis-textarea"
              value={text}
              onChange={e =>
                setText(e.target.value)
              }
              placeholder="Paste the suspicious message here..."
            />

          </label>


          <div className="example-row">

            {examples.map(
              example => (

                <button
                  key={example.label}
                  className="example-chip"
                  onClick={() =>
                    setText(
                      example.text,
                    )
                  }
                >
                  {example.label}
                </button>

              ),
            )}

          </div>


          <AnalyzeButton
            loading={loading}
            onClick={run}
            label="Analyze message"
          />

        </Panel>


        <Panel
          title="Detection coverage"
          kicker="SHARED INTELLIGENCE"
          icon={Sparkles}
        >

          <div className="coverage-list">

            <div>
              <KeyRound size={15} />
              <span>
                Credential & OTP requests
              </span>
            </div>

            <div>
              <AlertTriangle size={15} />
              <span>
                Social-engineering tactics
              </span>
            </div>

            <div>
              <Globe2 size={15} />
              <span>
                URLs & domains
              </span>
            </div>

            <div>
              <Shield size={15} />
              <span>
                Payment & UPI indicators
              </span>
            </div>

            <div>
              <Users size={15} />
              <span>
                Authority impersonation
              </span>
            </div>

          </div>

        </Panel>

      </div>


      <ErrorBox error={error} />


      {result && (
        <ReportView
          data={result}
        />
      )}

    </>
  );
}


// ============================================================
// WEB GUARD
// ============================================================

function WebGuard() {

  const meta =
    moduleMeta('web');


  const [url, setUrl] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  const [result, setResult] =
    useState<any>(null);


  const examples = [
    'https://www.paypal.com/signin',
    'https://sbi-login-security.xyz/verify-account',
    'https://secure-login.example.com/%2e%2e/account?verify=true',
  ];


  const run = async () => {

    if (!url.trim()) {

      setError(
        'Please enter a URL to analyze.',
      );

      return;
    }


    setLoading(true);
    setError('');
    setResult(null);


    try {

      const data =
        await post(
          '/webguard',
          {
            url,
            user_consent: true,
            resolve_dns: true,
          },
        );

      setResult(data);

    } catch (e: any) {

      setError(
        e.message ||
        'WebGuard analysis failed.',
      );

    } finally {

      setLoading(false);

    }

  };


  return (
    <>

      <PageHeader
        meta={meta}
        eyebrow="WEB INTELLIGENCE / DOMAIN ANALYSIS"
      />


      <div className="analyzer-layout">

        <Panel
          title="Inspect a URL"
          kicker="URL ANALYZER"
          icon={Globe2}
        >

          <label className="field-label">

            URL

            <input
              value={url}
              onChange={e =>
                setUrl(e.target.value)
              }
              placeholder="https://example.com/login"
            />

          </label>


          <div className="example-row">

            {examples.map(
              example => {

                let hostname =
                  example;

                try {
                  hostname =
                    new URL(
                      example,
                    ).hostname;
                } catch {
                  // Keep the original
                  // example if parsing fails.
                }


                return (
                  <button
                    key={example}
                    className="example-chip"
                    onClick={() =>
                      setUrl(example)
                    }
                  >
                    {hostname}
                  </button>
                );

              },
            )}

          </div>


          <AnalyzeButton
            loading={loading}
            onClick={run}
            label="Analyze URL"
          />

        </Panel>


        <Panel
          title="URL-level inspection"
          kicker="OBSERVABLE SIGNALS"
          icon={Search}
        >

          <div className="coverage-list">

            <div>
              <Globe2 size={15} />
              <span>
                Domain identity & structure
              </span>
            </div>

            <div>
              <ShieldCheck size={15} />
              <span>
                HTTPS & transport
              </span>
            </div>

            <div>
              <AlertTriangle size={15} />
              <span>
                Brand/domain mismatch
              </span>
            </div>

            <div>
              <Search size={15} />
              <span>
                DNS resolution
              </span>
            </div>

            <div>
              <Info size={15} />
              <span>
                Obfuscation & lookalikes
              </span>
            </div>

          </div>

        </Panel>

      </div>


      <ErrorBox error={error} />


      {result && (
        <ReportView
          data={result}
        />
      )}

    </>
  );
}


// ============================================================
// APP GUARD
// ============================================================

function AppGuard() {

  const meta =
    moduleMeta('app');


  const [appName, setAppName] =
    useState('');

  const [source, setSource] =
    useState('unknown');


  const [permissions, setPermissions] =
    useState({
      accessibility: false,
      overlay: false,
      screen_capture: false,
      sms: false,
      contacts: false,
      device_admin: false,
      remote_control: false,
    });


  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  const [result, setResult] =
    useState<any>(null);


  const examples = [
    'AnyDesk',
    'WhatsApp',
    'Unknown Remote Support App',
  ];


  const run = async () => {

    if (!appName.trim()) {

      setError(
        'Please enter an application name.',
      );

      return;
    }


    setLoading(true);
    setError('');
    setResult(null);


    try {

      const data =
        await post(
          '/appguard',
          {
            app_name: appName,
            installation_source: source,
            ...permissions,
            user_consent: true,
          },
        );

      setResult(data);

    } catch (e: any) {

      setError(
        e.message ||
        'AppGuard analysis failed.',
      );

    } finally {

      setLoading(false);

    }

  };


  const togglePermission = (
    key: keyof typeof permissions,
  ) => {

    setPermissions(prev => ({
      ...prev,
      [key]: !prev[key],
    }));

  };


  return (
    <>

      <PageHeader
        meta={meta}
        eyebrow="APPLICATION INTELLIGENCE / CAPABILITY ANALYSIS"
      />


      <div className="analyzer-layout">

        <Panel
          title="Inspect an application"
          kicker="APP PROVENANCE"
          icon={Smartphone}
        >

          <label className="field-label">

            Application name

            <input
              value={appName}
              onChange={e =>
                setAppName(
                  e.target.value,
                )
              }
              placeholder="Enter application name"
            />

          </label>


          <label className="field-label">

            Installation source

            <select
              value={source}
              onChange={e =>
                setSource(
                  e.target.value,
                )
              }
            >

              <option value="unknown">
                Unknown
              </option>

              <option value="play_store">
                Google Play Store
              </option>

              <option value="app_store">
                Apple App Store
              </option>

              <option value="official_website">
                Official website
              </option>

              <option value="third_party">
                Third-party source
              </option>

            </select>

          </label>


          <div className="permission-grid">

            {Object.entries(
              permissions,
            ).map(
              ([key, value]) => (

                <label
                  className={`permission-toggle ${value
                    ? 'selected'
                    : ''
                    }`}
                  key={key}
                >

                  <input
                    type="checkbox"
                    checked={value}
                    onChange={() =>
                      togglePermission(
                        key as keyof typeof permissions,
                      )
                    }
                  />

                  <span>

                    {key
                      .split("_")
                      .join(" ")
                      .replace(
                        /\b\w/g,
                        (char: string) =>
                          char.toUpperCase(),
                      )}

                  </span>

                </label>

              ),
            )}

          </div>


          <div className="example-row">

            {examples.map(
              example => (

                <button
                  key={example}
                  className="example-chip"
                  onClick={() =>
                    setAppName(
                      example,
                    )
                  }
                >
                  {example}
                </button>

              ),
            )}

          </div>


          <AnalyzeButton
            loading={loading}
            onClick={run}
            label="Analyze application"
          />

        </Panel>


        <Panel
          title="Capability signals"
          kicker="WHY PERMISSIONS MATTER"
          icon={ShieldAlert}
        >

          <div className="coverage-list">

            <div>
              <KeyRound size={15} />
              <span>
                Accessibility control
              </span>
            </div>

            <div>
              <Shield size={15} />
              <span>
                Overlay capability
              </span>
            </div>

            <div>
              <Smartphone size={15} />
              <span>
                Remote device control
              </span>
            </div>

            <div>
              <UploadCloud size={15} />
              <span>
                Screen capture
              </span>
            </div>

            <div>
              <AlertTriangle size={15} />
              <span>
                Credential/financial risk
              </span>
            </div>

          </div>

        </Panel>

      </div>


      <ErrorBox error={error} />


      {result && (
        <ReportView
          data={result}
        />
      )}

    </>
  );
}


// ============================================================
// PARENT GUARDIAN
// ============================================================

function ParentGuardian() {

  const meta =
    moduleMeta('parent');


  const [text, setText] =
    useState('');

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');

  const [result, setResult] =
    useState<any>(null);


  const [recording, setRecording] =
    useState(false);

  const [audioBlob, setAudioBlob] =
    useState<Blob | null>(null);

  const [audioUrl, setAudioUrl] =
    useState('');


  const mediaRecorderRef =
    useRef<MediaRecorder | null>(
      null,
    );

  const chunksRef =
    useRef<Blob[]>([]);


  useEffect(() => {

    return () => {

      if (audioUrl) {
        URL.revokeObjectURL(
          audioUrl,
        );
      }

    };

  }, [audioUrl]);


  // ----------------------------------------------------------
  // TEXT ANALYSIS
  // ----------------------------------------------------------

  const analyzeText = async () => {

    if (!text.trim()) {

      setError(
        'Enter a transcript or message before analysis.',
      );

      return;
    }


    setLoading(true);
    setError('');
    setResult(null);


    try {

      const data =
        await post(
          '/parentguardian',
          {
            text,
            user_consent: true,
          },
        );

      setResult(data);

    } catch (e: any) {

      setError(
        e.message ||
        'ParentGuardian analysis failed.',
      );

    } finally {

      setLoading(false);

    }

  };


  // ----------------------------------------------------------
  // START RECORDING
  // ----------------------------------------------------------

  const startRecording =
    async () => {

      setError('');

      if (
        !navigator.mediaDevices?.getUserMedia
      ) {

        setError(
          'Audio recording is not supported by this browser.',
        );

        return;
      }


      if (
        typeof MediaRecorder ===
        'undefined'
      ) {

        setError(
          'This browser does not support MediaRecorder.',
        );

        return;
      }


      try {

        const stream =
          await navigator.mediaDevices.getUserMedia(
            {
              audio: true,
            },
          );


        chunksRef.current = [];


        // Prefer WebM/Opus where supported.
        // Fall back to browser default otherwise.
        let recorder:
          MediaRecorder;


        if (
          MediaRecorder.isTypeSupported(
            'audio/webm;codecs=opus',
          )
        ) {

          recorder =
            new MediaRecorder(
              stream,
              {
                mimeType:
                  'audio/webm;codecs=opus',
              },
            );

        } else if (
          MediaRecorder.isTypeSupported(
            'audio/webm',
          )
        ) {

          recorder =
            new MediaRecorder(
              stream,
              {
                mimeType:
                  'audio/webm',
              },
            );

        } else {

          recorder =
            new MediaRecorder(
              stream,
            );

        }


        mediaRecorderRef.current =
          recorder;


        recorder.ondataavailable =
          event => {

            if (
              event.data.size >
              0
            ) {

              chunksRef.current.push(
                event.data,
              );

            }

          };


        recorder.onstop = () => {

          stream
            .getTracks()
            .forEach(track =>
              track.stop(),
            );


          const blob =
            new Blob(
              chunksRef.current,
              {
                type:
                  recorder.mimeType ||
                  'audio/webm',
              },
            );


          setAudioBlob(blob);


          setAudioUrl(prev => {

            if (prev) {
              URL.revokeObjectURL(
                prev,
              );
            }

            return URL.createObjectURL(
              blob,
            );

          });

        };


        recorder.start();

        setRecording(true);

      } catch (e: any) {

        setError(
          e.message ||
          'Microphone access was denied or unavailable.',
        );

      }

    };


  // ----------------------------------------------------------
  // STOP RECORDING
  // ----------------------------------------------------------

  const stopRecording = () => {

    const recorder =
      mediaRecorderRef.current;


    if (!recorder) {
      return;
    }


    if (
      recorder.state !==
      'inactive'
    ) {

      recorder.stop();

    }


    setRecording(false);

  };


  // ----------------------------------------------------------
  // AUDIO ANALYSIS
  // ----------------------------------------------------------

  const analyzeAudio =
    async () => {

      if (!audioBlob) {

        setError(
          'Record or upload audio first.',
        );

        return;
      }


      setLoading(true);
      setError('');
      setResult(null);


      try {

        const form =
          new FormData();


        form.append(
          'file',
          audioBlob,
          'parentguardian-recording.webm',
        );


        form.append(
          'user_consent',
          'true',
        );


        const res =
          await fetch(
            `${API}/api/v1/analyze/call/audio`,
            {
              method: 'POST',
              body: form,
            },
          );


        const data =
          await res
            .json()
            .catch(
              () => ({}),
            );


        // Backend may explicitly report
        // transcription unavailable.
        if (res.status === 501) {

          if (text.trim()) {

            const fallback =
              await post(
                '/parentguardian',
                {
                  text,
                  user_consent: true,
                },
              );


            setResult(
              fallback,
            );

            return;

          }


          throw new Error(
            'Audio transcription is unavailable on the server. Provide a transcript for analysis.',
          );

        }


        if (!res.ok) {

          throw new Error(
            typeof data?.detail ===
              'string'
              ? data.detail
              : 'Audio analysis failed.',
          );

        }


        setResult(data);

      } catch (e: any) {

        setError(
          e.message ||
          'Audio analysis failed.',
        );

      } finally {

        setLoading(false);

      }

    };


  return (
    <>

      <PageHeader
        meta={meta}
        eyebrow="FAMILY SAFETY / CONSENT-BASED REVIEW"
      />


      <div className="analyzer-layout">

        {/* TEXT / TRANSCRIPT */}

        <Panel
          title="Safety review"
          kicker="TEXT / TRANSCRIPT"
          icon={Users}
        >

          <label className="field-label">

            Message or transcript

            <textarea
              className="analysis-textarea"
              value={text}
              onChange={e =>
                setText(
                  e.target.value,
                )
              }
              placeholder="Paste a conversation or transcript. Example: “Don't tell your parents. Send me the OTP and delete these messages.”"
            />

          </label>


          <div className="privacy-notice">

            <Lock size={15} />

            <span>
              ParentGuardian is designed
              for transparent,
              consent-based review. It
              does not secretly monitor
              communications or diagnose
              abuse.
            </span>

          </div>


          <AnalyzeButton
            loading={loading}
            onClick={analyzeText}
            label="Analyze transcript"
          />

        </Panel>


        {/* AUDIO */}

        <Panel
          title="Record audio"
          kicker="USER-INITIATED MICROPHONE CAPTURE"
          icon={Mic}
        >

          <div className="recording-panel">

            <div
              className={`recording-orb ${recording
                ? 'recording'
                : ''
                }`}
            >
              <Mic size={25} />
            </div>


            <div>

              <b>
                {recording
                  ? 'Recording in progress'
                  : 'Ready to record'}
              </b>

              <small>
                Recording starts only
                after you press the
                button and grant
                microphone permission.
              </small>

            </div>

          </div>


          <div className="recording-actions">

            {!recording ? (

              <button
                className="secondary-button"
                onClick={
                  startRecording
                }
              >

                <Mic size={15} />

                Start recording

              </button>

            ) : (

              <button
                className="danger-button"
                onClick={
                  stopRecording
                }
              >

                <Square size={14} />

                Stop recording

              </button>

            )}


            {audioUrl && (

              <audio
                controls
                src={audioUrl}
                className="audio-player"
              />

            )}

          </div>


          {audioBlob && (

            <AnalyzeButton
              loading={loading}
              onClick={
                analyzeAudio
              }
              label="Analyze recorded audio"
            />

          )}

        </Panel>

      </div>


      <ErrorBox error={error} />


      {result && (
        <ReportView
          data={result}
        />
      )}

    </>
  );
}


// ============================================================
// REPORT GUARD
// ============================================================

function ReportGuard() {

  const meta =
    moduleMeta('report');


  const [channel, setChannel] =
    useState('sms');

  const [text, setText] =
    useState('');

  const [notes, setNotes] =
    useState('');

  const [consent, setConsent] =
    useState(true);


  const [submitted, setSubmitted] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState('');


  const run = async () => {

    if (!text.trim()) {

      setError(
        'Report content cannot be empty.',
      );

      return;
    }


    if (!consent) {

      setError(
        'Explicit consent is required before a report is stored in quarantine.',
      );

      return;
    }


    setLoading(true);
    setError('');
    setSubmitted(null);


    try {

      const result =
        await post(
          '/report',
          {
            text,
            channel,
            user_notes: notes,
            consent_anonymized_research:
              false,
            user_consent:
              consent,
          },
        );


      setSubmitted(result);

    } catch (e: any) {

      setError(
        e.message ||
        'Could not submit the report.',
      );

    } finally {

      setLoading(false);

    }

  };


  const evidence =
    submitted?.sanitization
      ?.observed_evidence ||
    [];


  const urls =
    submitted?.sanitization
      ?.security_entities_preserved
      ?.urls ||
    [];


  const redactions =
    submitted?.sanitization
      ?.redacted_counts ||
    {};


  const totalRedactions =
    Object.values(
      redactions,
    ).reduce(
      (
        total: number,
        value: unknown,
      ) =>
        total +
        Number(value || 0),
      0,
    );


  const hasRedactions =
    Object.values(
      redactions,
    ).some(
      (value: unknown) =>
        Number(value) > 0,
    );


  return (
    <>

      <PageHeader
        meta={meta}
        eyebrow="COMMUNITY INTELLIGENCE / QUARANTINE"
      />


      <div className="reportguard-layout">

        <Panel
          title="Submit suspicious activity"
          kicker="SERVER-SIDE SANITIZATION"
          icon={Flag}
        >

          <div className="report-flow">

            <div className="flow-step active">
              <span>1</span>
              <b>Describe</b>
            </div>

            <div className="flow-line" />

            <div className="flow-step">
              <span>2</span>
              <b>Sanitize</b>
            </div>

            <div className="flow-line" />

            <div className="flow-step">
              <span>3</span>
              <b>Quarantine</b>
            </div>

          </div>


          <label className="field-label">

            Source type

            <select
              value={channel}
              onChange={e =>
                setChannel(
                  e.target.value,
                )
              }
            >

              <option value="sms">
                SMS
              </option>

              <option value="whatsapp">
                WhatsApp
              </option>

              <option value="email">
                Email
              </option>

              <option value="payment_message">
                Payment message
              </option>

              <option value="social_message">
                Social message
              </option>

              <option value="call">
                Call
              </option>

            </select>

          </label>


          <label className="field-label">

            Suspicious content

            <textarea
              className="analysis-textarea"
              value={text}
              onChange={e =>
                setText(
                  e.target.value,
                )
              }
              placeholder="Paste the suspicious content. ReportGuard will redact common personal identifiers before quarantine; security URLs and threat indicators are preserved where possible."
            />

          </label>


          <label className="field-label">

            Reviewer note

            <input
              value={notes}
              onChange={e =>
                setNotes(
                  e.target.value,
                )
              }
              placeholder="Optional context for human review"
            />

          </label>


          <div className="report-privacy">

            <Lock size={15} />

            <span>

              <b>
                Quarantine boundary:
              </b>{' '}

              the server redacts common
              personal identifiers before
              storing the sanitized
              representation. It is not
              automatically added to
              training data.

            </span>

          </div>


          <label className="consent-row">

            <input
              type="checkbox"
              checked={consent}
              onChange={e =>
                setConsent(
                  e.target.checked,
                )
              }
            />

            <span>
              I authorize SentryMesh to
              store the sanitized report
              in the quarantine review
              workflow.
            </span>

          </label>


          <AnalyzeButton
            loading={loading}
            label="Sanitize & quarantine report"
            onClick={run}
          />

        </Panel>


        <Panel
          title="What happens next"
          kicker="REVIEW PIPELINE"
          icon={Network}
        >

          <div className="review-pipeline">

            <div>

              <span>01</span>

              <b>Sanitize</b>

              <small>
                Minimize unnecessary
                personal information.
              </small>

            </div>


            <div>

              <span>02</span>

              <b>Quarantine</b>

              <small>
                Keep reports separated
                from production training
                flows.
              </small>

            </div>


            <div>

              <span>03</span>

              <b>Review</b>

              <small>
                Human review can validate
                evidence and status.
              </small>

            </div>


            <div>

              <span>04</span>

              <b>Aggregate</b>

              <small>
                Useful patterns can inform
                community intelligence.
              </small>

            </div>

          </div>

        </Panel>

      </div>


      <ErrorBox error={error} />


      {submitted && (

        <section className="report-result-stack">

          {/* SUCCESS */}

          <div className="success-box report-success">

            <CheckCircle2 />

            <div>

              <b>
                Sanitized report quarantined
              </b>

              <span>
                {submitted.message ||
                  submitted.status ||
                  'Report accepted into quarantine.'}
              </span>

              <small className="receipt-id">

                Receipt: {submitted.report_id}

                {' • '}

                {submitted
                  .sanitization
                  ?.pii_detected
                  ? 'PII redaction applied'
                  : 'No common PII detected'}

                {' • '}

                training ingestion blocked

              </small>

            </div>

          </div>


          {/* STATUS + SANITIZATION */}

          <div className="report-result-grid">

            <Panel
              title="Quarantine status"
              kicker="AUDIT RECEIPT"
              icon={ShieldCheck}
            >

              <div className="report-meta-grid">

                <div>
                  <small>
                    REPORT ID
                  </small>

                  <b>
                    {submitted.report_id}
                  </b>
                </div>


                <div>

                  <small>
                    STATUS
                  </small>

                  <b className="status-text">

                    {String(
                      submitted.status ||
                      'pending_moderator_review',
                    ).split("_")
                      .join(" ")}

                  </b>

                </div>


                <div>

                  <small>
                    SOURCE
                  </small>

                  <b>
                    {submitted.channel}
                  </b>

                </div>


                <div>

                  <small>
                    TRAINING
                  </small>

                  <b>
                    BLOCKED
                  </b>

                </div>

              </div>


              <div className="report-boundary-note">

                <Lock size={14} />

                <span>

                  {submitted
                    .retention_note ||
                    'Only the sanitized quarantine representation is persisted by ReportGuard.'}

                </span>

              </div>

            </Panel>


            <Panel
              title="Sanitization evidence"
              kicker="WHAT WAS CHANGED"
              icon={FileCheck2}
            >

              <div className="redaction-summary">

                <div>

                  <b>
                    {totalRedactions}
                  </b>

                  <span>
                    identifiers redacted
                  </span>

                </div>


                <div>

                  <b>
                    {urls.length}
                  </b>

                  <span>
                    security URLs preserved
                  </span>

                </div>

              </div>


              <div className="evidence-list report-evidence">

                {Object.entries(
                  redactions,
                ).map(
                  (
                    [key, value],
                  ) =>
                    Number(value) >
                    0 && (

                      <EvidenceRow
                        key={key}
                        index={1}
                        title={key.split("_").join(" ")}
                        reason={`${value} identifier${Number(value) ===
                          1
                          ? ''
                          : 's'
                          } were detected and removed from the stored representation to minimize personal data.`}
                      />

                    ),
                )}


                {!hasRedactions && (

                  <div className="muted-box">
                    No common email,
                    phone, or UPI
                    identifiers were
                    detected.
                  </div>

                )}

              </div>

            </Panel>

          </div>


          {/* SECURITY EVIDENCE + SANITIZED REPORT */}

          <div className="report-result-grid">

            <Panel
              title="Observed security evidence"
              kicker="DESCRIPTIVE — NOT A FINAL VERDICT"
              icon={ShieldAlert}
            >

              <div className="evidence-list report-evidence">

                {evidence.length >
                  0 ? (

                  evidence.map(
                    (
                      item: any,
                      index: number,
                    ) => (

                      <EvidenceRow
                        key={index}
                        index={index + 1}
                        title={
                          item.signal ||
                          item.label ||
                          'Observed signal'
                        }
                        reason={
                          item.reason ||
                          'This signal was observed in the submitted report.'
                        }
                      />

                    ),
                  )

                ) : (

                  <div className="muted-box">
                    No additional
                    security-language
                    indicators were
                    extracted. The
                    report remains
                    available for
                    human review.
                  </div>

                )}

              </div>


              {urls.length > 0 && (

                <div className="preserved-evidence">

                  <b>
                    Preserved investigation
                    URLs
                  </b>


                  {urls.map(
                    (
                      item: string,
                    ) => (

                      <code key={item}>
                        {item}
                      </code>

                    ),
                  )}

                </div>

              )}

            </Panel>


            <Panel
              title="Sanitized report"
              kicker="SAFE REVIEW REPRESENTATION"
              icon={FileWarning}
            >

              <pre className="sanitized-report">

                {submitted.sanitized_text ||
                  'Sanitized content is unavailable.'}

              </pre>


              {submitted
                .sanitized_reviewer_note && (

                  <>

                    <div className="sanitized-note-label">
                      REVIEWER NOTE
                    </div>


                    <div className="sanitized-note">
                      {
                        submitted.sanitized_reviewer_note
                      }
                    </div>

                  </>

                )}

            </Panel>

          </div>


          {/* REVIEW STATUS */}

          <div className="report-review-state">

            <div>

              <span className="status-dot large" />

              <div>

                <b>
                  PENDING MODERATOR REVIEW
                </b>

                <small>
                  No human reviewer has
                  confirmed the report yet.
                  Evidence shown above
                  describes observed content
                  only.
                </small>

              </div>

            </div>


            <span>
              Training ingestion: blocked
            </span>

          </div>

        </section>

      )}

    </>
  );
}


// ============================================================
// MODEL OPS
// ============================================================

function ModelOps() {

  const meta =
    moduleMeta('ops');


  const [data, setData] =
    useState<any>(null);

  const [error, setError] =
    useState('');

  const [loading, setLoading] =
    useState(true);


  const load = async () => {

    setLoading(true);
    setError('');


    try {

      const result =
        await get('/model-ops');

      setData(result);

    } catch (e: any) {

      setError(
        e.message ||
        'Model Ops data could not be loaded.',
      );

    } finally {

      setLoading(false);

    }

  };


  useEffect(() => {

    void load();

  }, []);


  const models =
    data?.active_models || {};

  const artifacts =
    data?.artifacts || [];

  const evaluations =
    data?.evaluation_reports || [];


  const modelCount =
    Array.isArray(models)
      ? models.length
      : Object.keys(models).length;


  return (
    <>

      <PageHeader
        meta={meta}
        eyebrow="MODEL OPS / PLATFORM OBSERVABILITY"
      />


      <div className="ops-toolbar">

        <div>

          <span className="status-dot" />

          <b>
            MODEL REGISTRY
          </b>

          <small>
            Backend-reported model and
            evaluation metadata
          </small>

        </div>


        <button
          className="secondary-button"
          onClick={load}
          disabled={loading}
        >

          <RefreshCw size={14} />

          Refresh

        </button>

      </div>


      <ErrorBox error={error} />


      {loading ? (

        <div className="loading-box">

          <RefreshCw
            size={18}
            className="spin"
          />

          Loading model operations
          data...

        </div>

      ) : (

        <>

          <div className="ops-metrics">

            <div className="metric-card">

              <small>
                ACTIVE MODELS
              </small>

              <strong>
                {modelCount}
              </strong>

            </div>


            <div className="metric-card">

              <small>
                ARTIFACTS
              </small>

              <strong>
                {artifacts.length}
              </strong>

            </div>


            <div className="metric-card">

              <small>
                EVALUATIONS
              </small>

              <strong>
                {evaluations.length}
              </strong>

            </div>

          </div>


          <div className="result-grid">

            {/* ACTIVE MODELS */}

            <Panel
              title="Active models"
              kicker="MODEL REGISTRY"
              icon={Activity}
            >

              {Object.keys(models).length >
                0 ? (

                <div className="ops-list">

                  {Object.entries(
                    models,
                  ).map(
                    (
                      [
                        name,
                        value,
                      ]: [string, any],
                    ) => (

                      <div
                        className="ops-row"
                        key={name}
                      >

                        <div>

                          <b>
                            {name}
                          </b>

                          <small>

                            {typeof value ===
                              'string'
                              ? value
                              : value?.version ||
                              value?.path ||
                              'Registered model'}

                          </small>

                        </div>


                        <span className="ops-status">
                          ACTIVE
                        </span>

                      </div>

                    ),
                  )}

                </div>

              ) : (

                <div className="muted-box">
                  No active models were
                  reported by the backend.
                </div>

              )}

            </Panel>


            {/* EVALUATIONS */}

            <Panel
              title="Evaluation reports"
              kicker="MODEL QUALITY"
              icon={ClipboardCheck}
            >

              {evaluations.length >
                0 ? (

                <div className="ops-list">

                  {evaluations.map(
                    (
                      item: any,
                      index: number,
                    ) => (

                      <div
                        className="ops-row"
                        key={index}
                      >

                        <div>

                          <b>
                            {item?.name ||
                              item?.model ||
                              `Evaluation ${index + 1
                              }`}
                          </b>

                          <small>
                            {item?.date ||
                              item?.dataset ||
                              'Evaluation artifact'}
                          </small>

                        </div>

                      </div>

                    ),
                  )}

                </div>

              ) : (

                <div className="muted-box">
                  No evaluation reports were
                  reported by the backend.
                </div>

              )}

            </Panel>

          </div>


          {/* ARTIFACTS */}

          <Panel
            title="Artifacts"
            kicker="TRACEABILITY"
            icon={FileCheck2}
          >

            {artifacts.length >
              0 ? (

              <div className="ops-list">

                {artifacts.map(
                  (
                    item: any,
                    index: number,
                  ) => (

                    <div
                      className="ops-row"
                      key={index}
                    >

                      <div>

                        <b>
                          {item?.name ||
                            item?.model ||
                            `Artifact ${index + 1
                            }`}
                        </b>

                        <small>
                          {item?.path ||
                            item?.type ||
                            'Registered artifact'}
                        </small>

                      </div>

                    </div>

                  ),
                )}

              </div>

            ) : (

              <div className="muted-box">
                No model artifacts were
                reported.
              </div>

            )}

          </Panel>


          <div className="privacy-notice">

            <Info size={15} />

            <span>
              Model Ops displays
              backend-reported information
              only. SentryMesh does not
              invent model metrics, dataset
              statistics or evaluation
              results.
            </span>

          </div>

        </>

      )}

    </>
  );
}


// ============================================================
// COMMAND CENTER
// ============================================================

function Console() {

  const navigate =
    useNavigate();


  return (
    <div className="console-page">

      <div className="eyebrow">
        SENTRYMESH / COMMAND CENTER
      </div>


      <h1>
        Security intelligence at a glance.
      </h1>


      <p>
        Select an intelligence surface to
        investigate messages, domains,
        applications, family-safety signals
        or community reports.
      </p>


      <div className="console-grid">

        {MODULES.map(
          module => {

            const Icon =
              module.icon;


            return (
              <button
                key={module.key}
                className="console-card"
                onClick={() =>
                  navigate(
                    `/${module.key}`,
                  )
                }
              >

                <div className="console-icon">
                  <Icon size={19} />
                </div>


                <div>

                  <b>
                    {module.label}
                  </b>

                  <span>
                    {module.description}
                  </span>

                </div>


                <ArrowRight size={15} />

              </button>
            );

          },
        )}

      </div>

    </div>
  );
}


// ============================================================
// 404
// ============================================================

function NotFound() {

  const location =
    useLocation();


  return (
    <div className="empty-state">

      <CircleHelp size={28} />


      <div>

        <h2>
          Module not found
        </h2>

        <p>
          No SentryMesh route exists for{' '}

          <code>
            {location.pathname}
          </code>.

        </p>

      </div>


      <Link
        to="/"
        className="primary-button"
      >
        Return to command center
      </Link>

    </div>
  );
}


// ============================================================
// ROUTER
// ============================================================

function App() {

  return (
    <BrowserRouter>

      <AppShell>

        <Routes>

          {/* COMMAND CENTER */}
          <Route
            path="/"
            element={<Home />}
          />


          {/* INTELLIGENCE MODULES */}

          <Route
            path="/message"
            element={<MessageGuard />}
          />

          <Route
            path="/web"
            element={<WebGuard />}
          />

          <Route
            path="/app"
            element={<AppGuard />}
          />

          <Route
            path="/parent"
            element={<ParentGuardian />}
          />

          <Route
            path="/report"
            element={<ReportGuard />}
          />

          <Route
            path="/ops"
            element={<ModelOps />}
          />


          {/* PLATFORM */}

          <Route
            path="/privacy"
            element={<PrivacyPage />}
          />

          <Route
            path="/response"
            element={<ResponsePage />}
          />


          {/* LEGACY / COMMAND ROUTE */}

          <Route
            path="/console"
            element={<Console />}
          />


          {/* 404 */}

          <Route
            path="*"
            element={<NotFound />}
          />

        </Routes>

      </AppShell>

    </BrowserRouter>
  );
}


export default App;

