/* GitHub Pages: React + Recharts are globals from docs/index.html */
const { useState } = React;
const {
  BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, PieChart, Pie,
  Area, AreaChart, ReferenceLine, ComposedChart, ErrorBar,
} = Recharts;

// ============================================================================
// NOTE: Dashboard figures are static snapshots from data/results/*.json.
// The 6 LinguaLeap experiments use simulated data; Cookie Cats uses the real
// public dataset (90,189 players).  Re-run model/*.py to regenerate results.
// ============================================================================

// ============================================================================
// COLORS & STYLE
// ============================================================================
const COLORS = {
  primary: "#2563EB",
  positive: "#059669",
  negative: "#DC2626",
  negativeSoft: "#E87171",
  warning: "#D97706",
  neutral: "#6B7280",
  control: "#64748B",
  treatment: "#3B82F6",
  holdout: "#8B5CF6",
  bg: "#F8FAFC",
  card: "#FFFFFF",
  text: "#0F172A",
  subtext: "#64748B",
  border: "#E2E8F0",
};

// ============================================================================
// DATA — embedded analysis results
// ============================================================================
const EXPERIMENTS = [
  {
    id: "E1",
    name: "Social Login at Signup",
    area: "Acquisition",
    decision: "SHIP",
    decisionColor: COLORS.positive,
    primaryMetric: "Signup Completion Rate",
    rawLift: 9.24,
    pValue: 0.0001,
    sampleSize: 45000,
    teaching: "Textbook clean experiment",
    oneLine: "+9.24% signup completion, consistent across all segments",
    hypothesis: "Adding social login (Google/Apple) reduces signup friction and improves completion rate.",
    rawResult: { control: 61.6, treatment: 67.3, lift: 9.24, ci: [7.8, 10.6] },
    deeperFinding: "Effect present in every segment (country tier, device, traffic source). No SRM. P(T>C)=1.00.",
    segmentResults: [
      { segment: "Country: Tier 1", lift: 10.2 },
      { segment: "Country: Tier 2", lift: 8.5 },
      { segment: "Country: Tier 3", lift: 8.7 },
      { segment: "Device: iOS", lift: 9.7 },
      { segment: "Device: Android", lift: 8.9 },
      { segment: "Source: Organic", lift: 9.4 },
      { segment: "Source: Paid Social", lift: 8.2 },
      { segment: "Source: Paid Search", lift: 9.9 },
      { segment: "Source: Referral", lift: 10.4 },
    ],
  },
  {
    id: "E2",
    name: "Extended Trial 7→14 days",
    area: "Monetization",
    decision: "SHIP TO NEW USERS",
    decisionColor: COLORS.positive,
    primaryMetric: "Trial → Paid Conversion",
    rawLift: -4.04,
    pValue: 0.086,
    sampleSize: 38000,
    teaching: "Simpson's paradox — segment analysis flips the decision",
    oneLine: "Flat overall — but +22.9% for new users, -8% for tenured users",
    hypothesis: "Longer trial gives users more time to experience value, improving conversion.",
    rawResult: { control: 15.74, treatment: 15.10, lift: -4.04, ci: [-8.4, 0.6] },
    deeperFinding: "Overall flat masks opposing effects: new users +22.9% (p<0.01), returning -8.2% (p=0.04), tenured -8.0% (p<0.01).",
    segmentResults: [
      { segment: "New users (24% mix)", lift: 22.9 },
      { segment: "Returning (35% mix)", lift: -8.2 },
      { segment: "Tenured (40% mix)", lift: -8.0 },
    ],
    businessImpact: "Shipping to new users only: ~$216K projected annual incremental revenue from new-user conversion lift",
  },
  {
    id: "E3",
    name: "Push Time Shift (8am→8pm)",
    area: "Engagement",
    decision: "KILL",
    decisionColor: COLORS.negative,
    primaryMetric: "Daily Push Open Rate",
    rawLift: 7.2,
    pValue: 0.0001,
    sampleSize: 52000,
    teaching: "Novelty effect — short-term win decays into noise",
    oneLine: "Week 1 +14.6%. Week 4 +2.4%. Half-life: 1.1 weeks",
    hypothesis: "Evening pushes will outperform morning pushes due to lower competition for attention.",
    rawResult: { control: 18.0, treatment: 19.3, lift: 7.2, ci: [6.5, 7.9] },
    deeperFinding: "Lift decays exponentially. 1-week test would have shipped a +14.6% 'win'. 4-week test reveals true steady-state of ~2.4%.",
    weeklyDecay: [
      { week: 1, lift: 14.6 },
      { week: 2, lift: 9.0 },
      { week: 3, lift: 3.0 },
      { week: 4, lift: 2.4 },
    ],
    policyImplication: "Behavior-change tests (notifications, UI) require minimum 3-week runtime.",
  },
  {
    id: "E4",
    name: "Onboarding 5→3 steps",
    area: "Activation",
    decision: "KILL",
    decisionColor: COLORS.negative,
    primaryMetric: "D1 Activation Rate",
    rawLift: 12.16,
    pValue: 0.0001,
    sampleSize: 41000,
    teaching: "Primary metric wins, but North Star loses",
    oneLine: "D1 activation +12% looked great. D30 retention -9.5% killed it.",
    hypothesis: "Reducing onboarding friction will improve activation without harming retention.",
    rawResult: { control: 45.1, treatment: 50.6, lift: 12.16, ci: [10.5, 13.8] },
    deeperFinding: "Primary metric (D1) wins by +12.2%. Guardrail (D7) flat at +1.3%. North Star (D30) loses -9.5%. Net annual revenue impact: -$697K.",
    funnelMetrics: [
      { metric: "D1 Activation (Primary)", control: 45.1, treatment: 50.6, lift: 12.2 },
      { metric: "D7 Retention (Guardrail)", control: 25.4, treatment: 25.8, lift: 1.3 },
      { metric: "D30 Retention (North Star)", control: 11.5, treatment: 10.4, lift: -9.5 },
    ],
    businessImpact: "Net annual impact: -$697K. Lost retained users (-$1.1M) > gained marginal activations (+$417K).",
    policyImplication: "All activation tests must include D7 + D30 retention as pre-specified guardrail metrics.",
  },
  {
    id: "E5",
    name: "AI Conversation Practice",
    area: "Engagement",
    decision: "RE-RUN",
    decisionColor: COLORS.warning,
    primaryMetric: "14-day Sessions per User",
    rawLift: 2.61,
    pValue: 0.133,
    sampleSize: 6000,
    teaching: "p=0.13 ≠ no effect. Test was underpowered.",
    oneLine: "Observed +2.6%, post-hoc power only 31%. Not a null — undersized.",
    hypothesis: "AI conversation practice will increase engagement (sessions per user).",
    rawResult: { control: 8.49, treatment: 8.71, lift: 2.61, ci: [-0.8, 6.0] },
    deeperFinding: "MDE was set at 8% but realistic effect for engagement features is 2-5%. Sample size of 6,000 was sized for a much larger effect than this feature could plausibly produce.",
    powerAnalysis: {
      observedLift: 2.61,
      mdeDetectable: 4.9,
      mdeAtDesign: 8.0,
      sampleHad: 2907,
      sampleNeeded: 10417,
      postHocPower: 0.316,
    },
    policyImplication: "Default MDE for engagement features should be 3%, not 8%. Anchor MDE to historical effect sizes.",
  },
  {
    id: "E6",
    name: "Leaderboard Gamification",
    area: "Engagement",
    decision: "SHIP",
    decisionColor: COLORS.positive,
    primaryMetric: "Active Days in 30-Day Window",
    rawLift: 21.79,
    pValue: 0.0001,
    sampleSize: 58000,
    teaching: "Textbook rigor — CUPED + holdout + Bayesian all aligned",
    oneLine: "+22% DAU, validated by holdout, variance-reduced via CUPED",
    hypothesis: "Friends leaderboard increases daily engagement through social motivation.",
    rawResult: { control: 11.99, treatment: 14.60, lift: 21.79, ci: [20.1, 23.5] },
    deeperFinding: "CUPED reduced variance by 23%. Holdout group (n=5,866) confirmed control group is unbiased (C vs H lift = 0.4%). Bayesian P(T>C)=1.00, P(lift>20%)=1.00.",
    holdoutCheck: { controlVsHoldout: 0.39, interpretation: "PASSED" },
    cupedVarReduction: 23.3,
    bayesian: { probBetter: 1.0, probLiftAbove10: 1.0, probLiftAbove20: 0.95 },
    businessImpact: "Projected annual revenue lift: $10.7M (assumes 900K MAU, $0.15 ARPDAU)",
  },
];

// Cookie Cats data from real public dataset (90,189 players)
// Source: https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats
const COOKIE_CATS = {
  name: "Cookie Cats: Gate Placement",
  source: "Real public dataset — 90,189 mobile game players (Kaggle, CC0 license)",
  decision: "KEEP GATE AT LEVEL 30",
  background: "Cookie Cats is a popular puzzle game. The original gate was at level 30. Hypothesis: moving it to level 40 would improve retention by delaying friction.",
  sampleSizes: { gate_30: 44700, gate_40: 45489, total: 90189 },
  srm: { passed: true, pValue: 0.009 },
  retention1: { gate30: 44.82, gate40: 44.23, diff: -0.59, pValue: 0.074, significant: false, ci: [-1.24, 0.06] },
  retention7: { gate30: 19.02, gate40: 18.20, diff: -0.82, pValue: 0.002, significant: true, ci: [-1.33, -0.31] },
  bayesian: { d1ProbGate30Better: 0.962, d7ProbGate30Better: 0.999, probGate40LosesByOnePP: 0.243 },
  segmentation: [
    { tier: "No play", n: 3994, gate30: 0.83, gate40: 0.63, diff: -0.19 },
    { tier: "Tried (1-5)", n: 20723, gate30: 1.29, gate40: 1.44, diff: 0.15 },
    { tier: "Light (6-30)", n: 32845, gate30: 6.69, gate40: 6.13, diff: -0.56 },
    { tier: "Engaged (31-100)", n: 20242, gate30: 28.40, gate40: 26.23, diff: -2.18 },
    { tier: "Heavy (100+)", n: 12385, gate30: 71.39, gate40: 71.24, diff: -0.15 },
  ],
  insight: "Friction in the right place isn't bad. The forced wait at level 30 likely creates a habit-forming pause. Moving it to level 40 means more players hit the gate after they've already lost interest.",
};

const PORTFOLIO = {
  totalExperiments: 6,
  ship: 2, shipSegmented: 1, rerun: 1, kill: 2,
  shipRate: 33,
  totalUsersTested: 240000,
  patterns: [
    { name: "Primary vs North Star misalignment", expts: ["E4"], recommendation: "Activation tests must specify D7+D30 retention as guardrails", color: COLORS.negative },
    { name: "Novelty effect masking steady-state", expts: ["E3"], recommendation: "Behavior-change tests require minimum 3-week runtime", color: COLORS.warning },
    { name: "Underpowered test producing false null", expts: ["E5"], recommendation: "Default MDE for engagement features should be 3%, not 8%", color: COLORS.warning },
    { name: "Simpson's paradox in pooled analysis", expts: ["E2"], recommendation: "Tenure-based segment analysis standard for monetization tests", color: COLORS.treatment },
  ],
  programPnL: {
    revenueFromShips: "$10.9M+",
    revenueDetail: "E6: $10.7M projected · E2: $216K new-user segment",
    damagePrevented: "$697K",
    damageDetail: "E4 kill prevented D30 retention loss",
  },
  counterFactuals: [
    { id: "E2", verb: "would have been killed", surface: "−4% overall conversion", reality: "+22.9% for new users (Simpson's paradox)", cost: "$216K/yr left on the table" },
    { id: "E3", verb: "would have been shipped", surface: "+7.2% push open rate", reality: "Novelty effect — true steady-state lift only +2.4%", cost: "Deployed a decaying metric as permanent win" },
    { id: "E4", verb: "would have been shipped", surface: "+12% D1 activation", reality: "D30 retention −9.5%", cost: "−$697K/yr in retention damage" },
  ],
};

// ============================================================================
// REUSABLE COMPONENTS
// ============================================================================
const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl border border-slate-200 p-5 shadow-sm ${className}`}>
    {children}
  </div>
);

const StatCard = ({ label, value, sub, color }) => (
  <Card>
    <div className="text-xs font-medium uppercase tracking-wider text-gray-400">{label}</div>
    <div className="text-2xl font-bold mt-1" style={{ color: color || COLORS.text }}>{value}</div>
    {sub && <div className="text-xs text-gray-400 mt-0.5">{sub}</div>}
  </Card>
);

const Pill = ({ text, color, bgColor }) => (
  <span className="px-2.5 py-1 rounded-full text-xs font-bold inline-block"
    style={{ color, backgroundColor: bgColor }}>
    {text}
  </span>
);

const SectionTitle = ({ children, className = "" }) => (
  <h3 className={`text-sm font-bold uppercase tracking-wider text-gray-500 mb-3 ${className}`}>
    {children}
  </h3>
);

// ============================================================================
// TAB 1: PROGRAM DASHBOARD
// ============================================================================
const ProgramDashboard = ({ onSelectExperiment }) => {
  const decisionData = [
    { name: "Ship", value: PORTFOLIO.ship, color: COLORS.positive },
    { name: "Ship to segment", value: PORTFOLIO.shipSegmented, color: "#34D399" },
    { name: "Re-run", value: PORTFOLIO.rerun, color: COLORS.warning },
    { name: "Kill", value: PORTFOLIO.kill, color: COLORS.negative },
  ];

  const liftData = EXPERIMENTS.map(e => ({
    name: e.id,
    fullName: e.name,
    lift: e.id === "E2" ? 22.9 : e.id === "E4" ? -9.5 : e.rawLift,
    decision: e.decision,
    color: e.decisionColor,
  }));

  return (
    <div className="space-y-6">
      {/* Hero KPIs — dark */}
      <div className="rounded-xl px-7 py-6" style={{ backgroundColor: "#1E293B" }}>
        <h2 className="text-xl font-bold text-white">Q3 2025 Experimentation Review</h2>
        <div className="grid grid-cols-3 gap-x-10 gap-y-6 mt-5 pt-5" style={{ borderTop: "1px solid rgba(255,255,255,0.1)" }}>
          {[
            { value: "6", label: "Experiments Run", color: "#fff" },
            { value: "33%", label: "Ship Rate", color: "#34D399" },
            { value: "240K", label: "Users Tested", color: "#fff" },
            { value: "$10.9M+", label: "Revenue from Ships", color: "#34D399" },
            { value: "$697K", label: "Damage Prevented", color: "#FCA5A5" },
            { value: "3 of 6", label: "Wrong Calls Prevented", color: "#93C5FD" },
          ].map((s, i) => (
            <div key={i}>
              <div className="text-4xl font-bold" style={{ color: s.color }}>{s.value}</div>
              <div className="text-base text-slate-400 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Counter-factual: Decision Quality — white */}
      <Card>
        <SectionTitle>Without Rigorous Analysis, Half These Experiments Would Have Been Decided Wrong</SectionTitle>
        <div className="grid grid-cols-3 gap-4 mt-2">
          {PORTFOLIO.counterFactuals.map(cf => {
            const accent = cf.id === "E2" ? { bg: "#FFFBEB", border: "#FDE68A", badge: "#D97706" }
              : cf.id === "E3" ? { bg: "#FFF7ED", border: "#FED7AA", badge: "#EA580C" }
              : { bg: "#FFF1F2", border: "#FECDD3", badge: "#E11D48" };
            return (
              <div key={cf.id} className="p-4 rounded-lg border" style={{ backgroundColor: accent.bg, borderColor: accent.border }}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-mono text-xs px-1.5 py-0.5 rounded font-bold text-white"
                    style={{ backgroundColor: accent.badge }}>{cf.id}</span>
                  <span className="text-xs font-bold text-slate-700">{cf.verb}</span>
                </div>
                <div className="text-xs text-slate-600 space-y-1">
                  <div><span className="font-semibold text-slate-700">Surface read:</span> {cf.surface}</div>
                  <div><span className="font-semibold text-slate-700">Deeper truth:</span> {cf.reality}</div>
                  <div className="font-bold pt-1.5 mt-1.5 text-slate-900" style={{ borderTop: `1px solid ${accent.border}` }}>
                    → {cf.cost}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-4 px-4 py-3 bg-slate-50 rounded-lg">
          <p className="text-xs text-slate-600 leading-relaxed">
            The value of an experimentation program isn't just the features it ships — it's the <span className="font-bold text-slate-800">bad decisions it prevents</span>.
          </p>
        </div>
      </Card>

      {/* Two main charts */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <SectionTitle>Decision Breakdown</SectionTitle>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={decisionData} dataKey="value" innerRadius={60} outerRadius={100}
                paddingAngle={2} label={({ name, value }) => `${name}: ${value}`}>
                {decisionData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 px-4 py-3 bg-blue-50 rounded-lg border border-blue-100">
            <p className="text-xs text-blue-900 font-medium leading-relaxed">
              Healthy pattern. Teams shipping &gt;80% of experiments aren't experimenting — they're rubber-stamping. Teams shipping &lt;10% are over-investing in low-impact tests.
            </p>
          </div>
        </Card>

        <Card>
          <SectionTitle>Lift by Experiment (Key Metric)</SectionTitle>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={liftData} margin={{ top: 20, right: 10, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
              <XAxis dataKey="name" stroke={COLORS.subtext} />
              <YAxis stroke={COLORS.subtext} unit="%" />
              <Tooltip cursor={{ fill: "rgba(0,0,0,0.05)" }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div className="bg-white p-3 rounded shadow-lg border text-xs">
                      <div className="font-bold">{d.fullName}</div>
                      <div>Lift: {d.lift > 0 ? "+" : ""}{d.lift}%</div>
                      <div className="font-bold mt-1" style={{ color: d.color }}>{d.decision}</div>
                    </div>
                  );
                }}
              />
              <ReferenceLine y={0} stroke="#374151" />
              <Bar dataKey="lift" radius={[6, 6, 0, 0]}>
                {liftData.map((entry, i) => <Cell key={i} fill={entry.color} fillOpacity={0.85} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-3 text-xs text-gray-400 text-center">
            E2 shown as new-user lift (+22.9%); E4 shown as D30 retention (-9.5%)
          </div>
        </Card>
      </div>

      {/* Experiment list */}
      <Card>
        <SectionTitle>The Quarter in One Chart</SectionTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left">
                <th className="py-3 px-2 text-xs uppercase tracking-wider text-gray-400 font-medium">#</th>
                <th className="py-3 px-2 text-xs uppercase tracking-wider text-gray-400 font-medium">Experiment</th>
                <th className="py-3 px-2 text-xs uppercase tracking-wider text-gray-400 font-medium">Area</th>
                <th className="py-3 px-2 text-xs uppercase tracking-wider text-gray-400 font-medium">Surface Read</th>
                <th className="py-3 px-2 text-xs uppercase tracking-wider text-gray-400 font-medium">Decision</th>
                <th className="py-3 px-2 text-xs uppercase tracking-wider text-gray-400 font-medium">Why</th>
              </tr>
            </thead>
            <tbody>
              {EXPERIMENTS.map(e => (
                <tr key={e.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSelectExperiment(e.id)}>
                  <td className="py-3 px-2 text-gray-400 font-mono">{e.id}</td>
                  <td className="py-3 px-2 font-medium text-gray-900">{e.name}</td>
                  <td className="py-3 px-2 text-gray-500">{e.area}</td>
                  <td className="py-3 px-2 text-gray-700">
                    {e.rawLift > 0 ? "+" : ""}{e.rawLift}%, p={e.pValue < 0.001 ? "<0.001" : e.pValue.toFixed(3)}
                  </td>
                  <td className="py-3 px-2">
                    <Pill text={e.decision} color={e.decisionColor} bgColor={`${e.decisionColor}20`} />
                  </td>
                  <td className="py-3 px-2 text-xs text-gray-600 max-w-md">{e.oneLine}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-gray-400 mt-3 italic">Click any row to view experiment detail →</p>
      </Card>

      {/* Cross-experiment patterns */}
      <Card>
        <SectionTitle>Cross-Experiment Patterns → Next Quarter's Policy</SectionTitle>
        <div className="space-y-3">
          {PORTFOLIO.patterns.map((p, i) => (
            <div key={i} className="p-4 rounded-lg border border-gray-200 flex items-start gap-4"
              style={{ backgroundColor: `${p.color}08` }}>
              <div className="flex-shrink-0 w-1.5 h-12 rounded-full" style={{ backgroundColor: p.color }} />
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div className="font-bold text-gray-900">{p.name}</div>
                  <span className="text-xs text-gray-400">Found in: {p.expts.join(", ")}</span>
                </div>
                <div className="text-sm text-gray-600 mt-1">→ {p.recommendation}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Signature insight */}
      <div className="rounded-xl p-6 border-2 border-blue-200" style={{ backgroundColor: "#EFF6FF" }}>
        <div className="text-xs font-bold uppercase tracking-wider text-blue-700 mb-2">
          The quarter in one sentence
        </div>
        <p className="text-base text-blue-900 leading-relaxed">
          Out of 6 experiments, only 2 shipped unconditionally — and 3 would have been decided incorrectly based on surface-level analysis alone. <span className="font-bold">The real ROI of an experimentation program isn't the features it ships — it's the bad decisions it prevents and the organizational learning it creates.</span>
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// TAB 2: EXPERIMENT GALLERY
// ============================================================================
const ExperimentGallery = ({ selectedId, onSelect }) => {
  const exp = EXPERIMENTS.find(e => e.id === selectedId) || EXPERIMENTS[0];

  return (
    <div className="space-y-6">
      {/* Selector */}
      <div className="grid grid-cols-3 gap-3">
        {EXPERIMENTS.map(e => (
          <button key={e.id}
            onClick={() => onSelect(e.id)}
            className={`text-left px-4 py-3 rounded-xl transition-all ${
              e.id === selectedId
                ? "bg-gray-900 text-white shadow-lg ring-2 ring-gray-900 ring-offset-2"
                : "bg-white text-gray-700 border border-gray-200 hover:border-gray-400 hover:shadow-sm"
            }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`font-mono text-xs font-bold px-1.5 py-0.5 rounded ${
                  e.id === selectedId ? "bg-white/20 text-white" : "bg-gray-100 text-gray-500"
                }`}>{e.id}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  e.id === selectedId ? "bg-white/15 text-gray-300" : "bg-gray-50 text-gray-400"
                }`}>{e.area}</span>
              </div>
              <Pill text={e.decision}
                color={e.id === selectedId ? "#fff" : e.decisionColor}
                bgColor={e.id === selectedId ? "rgba(255,255,255,0.15)" : `${e.decisionColor}15`} />
            </div>
            <div className={`text-sm font-semibold mt-2 ${e.id === selectedId ? "text-white" : "text-gray-900"}`}>
              {e.name}
            </div>
          </button>
        ))}
      </div>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-400">{exp.area} · {exp.id}</div>
          <h2 className="text-2xl font-bold text-gray-900 mt-1">{exp.name}</h2>
          <p className="text-sm text-gray-600 mt-2 max-w-2xl">{exp.oneLine}</p>
        </div>
        <Pill text={exp.decision} color={exp.decisionColor} bgColor={`${exp.decisionColor}20`} />
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Primary Metric" value={exp.primaryMetric} />
        <StatCard label="Sample Size" value={exp.sampleSize.toLocaleString()} />
        <StatCard label="Surface Lift"
          value={`${exp.rawLift > 0 ? "+" : ""}${exp.rawLift}%`}
          color={exp.rawLift > 0 ? COLORS.positive : COLORS.negative} />
        <StatCard label="P-value" value={exp.pValue < 0.001 ? "<0.001" : exp.pValue.toFixed(3)} />
      </div>

      {/* Hypothesis & Finding */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <SectionTitle>Hypothesis</SectionTitle>
          <p className="text-sm text-gray-700 leading-relaxed">{exp.hypothesis}</p>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="text-xs uppercase tracking-wider text-gray-400 mb-1">Initial Read</div>
            <p className="text-sm text-gray-700">
              {exp.rawLift > 0 ? "+" : ""}{exp.rawLift}%, p={exp.pValue < 0.001 ? "<0.001" : exp.pValue.toFixed(3)}, 95% CI: [{exp.rawResult.ci[0]}%, {exp.rawResult.ci[1]}%]
            </p>
          </div>
        </Card>

        <Card>
          <SectionTitle>Deeper Finding</SectionTitle>
          <p className="text-sm text-gray-700 leading-relaxed">{exp.deeperFinding}</p>
          {exp.policyImplication && (
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="text-xs uppercase tracking-wider text-gray-400 mb-1">Policy Implication</div>
              <p className="text-sm text-gray-700 italic">→ {exp.policyImplication}</p>
            </div>
          )}
        </Card>
      </div>

      {/* Per-experiment specific viz */}
      {exp.id === "E1" && <E1Viz exp={exp} />}
      {exp.id === "E2" && <E2Viz exp={exp} />}
      {exp.id === "E3" && <E3Viz exp={exp} />}
      {exp.id === "E4" && <E4Viz exp={exp} />}
      {exp.id === "E5" && <E5Viz exp={exp} />}
      {exp.id === "E6" && <E6Viz exp={exp} />}

      {/* Teaching moment */}
      <div className="rounded-xl p-5 border-2" style={{
        backgroundColor: `${exp.decisionColor}08`,
        borderColor: `${exp.decisionColor}40`,
      }}>
        <div className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: exp.decisionColor }}>
          Teaching Moment
        </div>
        <p className="text-base font-medium text-gray-900">{exp.teaching}</p>
      </div>
    </div>
  );
};

// E1: Segment consistency
const E1Viz = ({ exp }) => (
  <Card>
    <SectionTitle>Segment Consistency — effect present in every segment</SectionTitle>
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={exp.segmentResults} layout="vertical" margin={{ left: 80 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis type="number" stroke={COLORS.subtext} unit="%" />
        <YAxis type="category" dataKey="segment" stroke={COLORS.subtext} width={150} fontSize={11} />
        <Tooltip />
        <ReferenceLine x={exp.rawLift} stroke={COLORS.positive} strokeDasharray="5 5"
          label={{ value: `Overall: +${exp.rawLift}%`, position: "right", fill: COLORS.positive, fontSize: 11 }} />
        <Bar dataKey="lift" fill={COLORS.treatment} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  </Card>
);

// E2: Simpson's Paradox
const E2Viz = ({ exp }) => (
  <div className="space-y-6">
    <Card>
      <SectionTitle>Simpson's Paradox — The Average Lies</SectionTitle>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={[
          { name: "Overall", lift: -4.04, color: COLORS.neutral },
          { name: "New users", lift: 22.9, color: COLORS.positive },
          { name: "Returning", lift: -8.2, color: COLORS.negative },
          { name: "Tenured", lift: -8.0, color: COLORS.negative },
        ]}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
          <XAxis dataKey="name" stroke={COLORS.subtext} />
          <YAxis stroke={COLORS.subtext} unit="%" />
          <Tooltip />
          <ReferenceLine y={0} stroke="#374151" />
          <Bar dataKey="lift" radius={[6, 6, 0, 0]}>
            {[COLORS.neutral, COLORS.positive, COLORS.negative, COLORS.negative].map((c, i) =>
              <Cell key={i} fill={c} fillOpacity={0.85} />
            )}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>

    <Card>
      <SectionTitle>Business Impact (if shipped to new users only)</SectionTitle>
      <p className="text-sm text-gray-700">{exp.businessImpact}</p>
    </Card>
  </div>
);

// E3: Novelty decay
const E3Viz = ({ exp }) => (
  <div className="grid grid-cols-2 gap-6">
    <Card>
      <SectionTitle>Lift Decay Over 4 Weeks</SectionTitle>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={exp.weeklyDecay}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
          <XAxis dataKey="week" stroke={COLORS.subtext} tickFormatter={w => `W${w}`} />
          <YAxis stroke={COLORS.subtext} unit="%" />
          <Tooltip />
          <ReferenceLine y={3} stroke={COLORS.warning} strokeDasharray="4 4"
            label={{ value: "Ship threshold", fill: COLORS.warning, fontSize: 10, position: "right" }} />
          <Area type="monotone" dataKey="lift" stroke={COLORS.treatment} fill={COLORS.treatment} fillOpacity={0.3} strokeWidth={2.5} />
        </AreaChart>
      </ResponsiveContainer>
    </Card>

    <Card>
      <SectionTitle>What If We Stopped Earlier?</SectionTitle>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={[
          { name: "1-week", lift: 14.6, ship: true },
          { name: "2-week", lift: 11.8, ship: true },
          { name: "3-week", lift: 8.8, ship: true },
          { name: "4-week (actual)", lift: 7.2, ship: true },
        ]}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
          <XAxis dataKey="name" stroke={COLORS.subtext} fontSize={11} />
          <YAxis stroke={COLORS.subtext} unit="%" />
          <Tooltip />
          <ReferenceLine y={3} stroke={COLORS.warning} strokeDasharray="4 4" />
          <Bar dataKey="lift" fill={COLORS.negative} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-2 italic">Any duration shorter than 3 weeks would have shipped a dud.</p>
    </Card>
  </div>
);

// E4: Funnel divergence
const E4Viz = ({ exp }) => (
  <div className="space-y-6">
    <Card>
      <SectionTitle>Funnel Metrics — Primary Wins, North Star Loses</SectionTitle>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={exp.funnelMetrics} margin={{ top: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
          <XAxis dataKey="metric" stroke={COLORS.subtext} fontSize={11} />
          <YAxis stroke={COLORS.subtext} unit="%" />
          <Tooltip />
          <Legend />
          <Bar dataKey="control" name="Control" fill={COLORS.control} radius={[4, 4, 0, 0]} />
          <Bar dataKey="treatment" name="Treatment" fill={COLORS.treatment} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>

    <Card>
      <SectionTitle>Net Annual Revenue Impact</SectionTitle>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={[
          { name: "Revenue from extra activations", value: 417, color: COLORS.positive },
          { name: "Revenue lost from retention decline", value: -1115, color: COLORS.negative },
          { name: "NET annual revenue impact", value: -697, color: COLORS.negative },
        ]}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
          <XAxis dataKey="name" stroke={COLORS.subtext} fontSize={11} />
          <YAxis stroke={COLORS.subtext} tickFormatter={v => `$${v}K`} />
          <Tooltip formatter={v => `$${v}K`} />
          <ReferenceLine y={0} stroke="#374151" />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {[COLORS.positive, COLORS.negative, COLORS.negative].map((c, i) =>
              <Cell key={i} fill={c} fillOpacity={0.85} />
            )}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-sm text-gray-700 mt-3">{exp.businessImpact}</p>
    </Card>
  </div>
);

// E5: Power analysis
const E5Viz = ({ exp }) => {
  const p = exp.powerAnalysis;
  return (
    <div className="grid grid-cols-2 gap-6">
      <Card>
        <SectionTitle>Effect Size Mismatch</SectionTitle>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={[
            { name: "Observed lift", value: p.observedLift, color: COLORS.treatment },
            { name: "MDE we could detect (80% power)", value: p.mdeDetectable, color: COLORS.warning },
            { name: "MDE we sized for (at design)", value: p.mdeAtDesign, color: COLORS.negative },
          ]} layout="vertical" margin={{ left: 100 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis type="number" stroke={COLORS.subtext} unit="%" />
            <YAxis type="category" dataKey="name" stroke={COLORS.subtext} width={180} fontSize={10} />
            <Tooltip />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {[COLORS.treatment, COLORS.warning, COLORS.negative].map((c, i) =>
                <Cell key={i} fill={c} fillOpacity={0.85} />
              )}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card>
        <SectionTitle>Sample Size Required</SectionTitle>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={[
            { name: "What we had (per variant)", value: p.sampleHad, color: COLORS.negative },
            { name: "What we needed (80% power)", value: p.sampleNeeded, color: COLORS.positive },
          ]}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="name" stroke={COLORS.subtext} fontSize={11} />
            <YAxis stroke={COLORS.subtext} />
            <Tooltip />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {[COLORS.negative, COLORS.positive].map((c, i) =>
                <Cell key={i} fill={c} fillOpacity={0.85} />
              )}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
          <p className="text-xs text-amber-900">
            <span className="font-bold">Post-hoc power: {(p.postHocPower * 100).toFixed(0)}%.</span> We needed {Math.round(p.sampleNeeded / p.sampleHad)}× more users to detect this effect with confidence.
          </p>
        </div>
      </Card>
    </div>
  );
};

// E6: CUPED + Bayesian + Holdout
const E6Viz = ({ exp }) => (
  <div className="grid grid-cols-3 gap-6">
    <Card>
      <SectionTitle>Holdout Validation</SectionTitle>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={[
          { name: "Control", value: 11.99, color: COLORS.control },
          { name: "Treatment", value: 14.60, color: COLORS.treatment },
          { name: "Holdout", value: 11.94, color: COLORS.holdout },
        ]}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
          <XAxis dataKey="name" stroke={COLORS.subtext} />
          <YAxis stroke={COLORS.subtext} />
          <Tooltip />
          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {[COLORS.control, COLORS.treatment, COLORS.holdout].map((c, i) =>
              <Cell key={i} fill={c} fillOpacity={0.85} />
            )}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-500 mt-2">Control vs Holdout: {exp.holdoutCheck.controlVsHoldout}% — {exp.holdoutCheck.interpretation}</p>
    </Card>

    <Card>
      <SectionTitle>CUPED Variance Reduction</SectionTitle>
      <div className="flex items-center justify-center h-48">
        <div className="text-center">
          <div className="text-5xl font-bold text-blue-600">{exp.cupedVarReduction}%</div>
          <div className="text-sm text-gray-500 mt-2">variance reduction</div>
          <div className="text-xs text-gray-400 mt-3 max-w-xs">
            ≈ same precision as running with 30% more users at standard analysis
          </div>
        </div>
      </div>
    </Card>

    <Card>
      <SectionTitle>Bayesian Probabilities</SectionTitle>
      <div className="space-y-4 mt-4">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span>P(Treatment &gt; Control)</span>
            <span className="font-bold">{exp.bayesian.probBetter}</span>
          </div>
          <div className="bg-gray-100 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${exp.bayesian.probBetter * 100}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span>P(lift &gt; 10%)</span>
            <span className="font-bold">{exp.bayesian.probLiftAbove10}</span>
          </div>
          <div className="bg-gray-100 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${exp.bayesian.probLiftAbove10 * 100}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span>P(lift &gt; 20%)</span>
            <span className="font-bold">{exp.bayesian.probLiftAbove20}</span>
          </div>
          <div className="bg-gray-100 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${exp.bayesian.probLiftAbove20 * 100}%` }} />
          </div>
        </div>
      </div>
    </Card>
  </div>
);

// ============================================================================
// TAB 3: COOKIE CATS DEEP DIVE
// ============================================================================
const CookieCatsDeepDive = () => {
  const cc = COOKIE_CATS;
  return (
    <div className="space-y-6">
      <div>
        <div className="text-xs uppercase tracking-wider text-gray-400">Real-world data deep dive</div>
        <h2 className="text-2xl font-bold text-gray-900 mt-1">{cc.name}</h2>
        <p className="text-sm text-gray-500 mt-1">{cc.source}</p>
      </div>

      {/* Background */}
      <Card>
        <SectionTitle>Background</SectionTitle>
        <p className="text-sm text-gray-700 leading-relaxed">{cc.background}</p>
      </Card>

      {/* Decision banner */}
      <div className="rounded-xl p-5 border-2 border-blue-200 bg-blue-50">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-blue-700 mb-1">Decision</div>
            <div className="text-xl font-bold text-blue-900">{cc.decision}</div>
          </div>
          <div className="text-right">
            <div className="text-xs uppercase tracking-wider text-blue-700">Confidence</div>
            <div className="text-sm font-bold text-blue-900">HIGH (Bayesian P &gt; 99%)</div>
          </div>
        </div>
      </div>

      {/* Sample & SRM */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total Players" value={cc.sampleSizes.total.toLocaleString()} />
        <StatCard label="gate_30 (control)" value={cc.sampleSizes.gate_30.toLocaleString()} sub="49.6%" />
        <StatCard label="gate_40 (treatment)" value={cc.sampleSizes.gate_40.toLocaleString()} sub="50.4%" />
      </div>

      {/* Retention comparison */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <SectionTitle>1-Day Retention</SectionTitle>
          <div className="text-xs text-gray-500 mb-3">NOT significantly different (p={cc.retention1.pValue})</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={[
              { name: "gate_30", value: cc.retention1.gate30, color: COLORS.treatment },
              { name: "gate_40", value: cc.retention1.gate40, color: COLORS.negative },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
              <XAxis dataKey="name" stroke={COLORS.subtext} />
              <YAxis stroke={COLORS.subtext} domain={[40, 50]} unit="%" />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                <Cell fill={COLORS.treatment} fillOpacity={0.85} />
                <Cell fill={COLORS.negative} fillOpacity={0.85} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-3 text-xs text-gray-500">
            Δ = {cc.retention1.diff}pp · 95% CI: [{cc.retention1.ci[0]}pp, {cc.retention1.ci[1]}pp]
          </div>
        </Card>

        <Card>
          <SectionTitle>7-Day Retention</SectionTitle>
          <div className="text-xs text-red-600 font-semibold mb-3">SIGNIFICANTLY LOWER for gate_40 (p={cc.retention7.pValue})</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={[
              { name: "gate_30", value: cc.retention7.gate30, color: COLORS.treatment },
              { name: "gate_40", value: cc.retention7.gate40, color: COLORS.negative },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
              <XAxis dataKey="name" stroke={COLORS.subtext} />
              <YAxis stroke={COLORS.subtext} domain={[17, 20]} unit="%" />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                <Cell fill={COLORS.treatment} fillOpacity={0.85} />
                <Cell fill={COLORS.negative} fillOpacity={0.85} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-3 text-xs text-red-600 font-semibold">
            Δ = {cc.retention7.diff}pp · 95% CI: [{cc.retention7.ci[0]}pp, {cc.retention7.ci[1]}pp]
          </div>
        </Card>
      </div>

      {/* Bayesian probabilities */}
      <Card>
        <SectionTitle>Bayesian Posterior Probabilities</SectionTitle>
        <div className="space-y-4 mt-3">
          {[
            { label: "P(gate_30 better at day 1)", value: cc.bayesian.d1ProbGate30Better, color: COLORS.neutral },
            { label: "P(gate_30 better at day 7)", value: cc.bayesian.d7ProbGate30Better, color: COLORS.treatment },
            { label: "P(gate_40 hurts retention by ≥1pp at D7)", value: cc.bayesian.probGate40LosesByOnePP, color: COLORS.warning },
          ].map((b, i) => (
            <div key={i}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-700">{b.label}</span>
                <span className="font-bold" style={{ color: b.color }}>{b.value.toFixed(3)}</span>
              </div>
              <div className="bg-gray-100 rounded-full h-3">
                <div className="rounded-full h-3" style={{ width: `${b.value * 100}%`, backgroundColor: b.color }} />
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Engagement segmentation */}
      <Card>
        <SectionTitle>7-Day Retention by Engagement Tier</SectionTitle>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={cc.segmentation}>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="tier" stroke={COLORS.subtext} fontSize={10} />
            <YAxis stroke={COLORS.subtext} unit="%" />
            <Tooltip />
            <Legend />
            <Bar dataKey="gate30" name="gate_30" fill={COLORS.treatment} fillOpacity={0.85} radius={[4, 4, 0, 0]} />
            <Bar dataKey="gate40" name="gate_40" fill={COLORS.negative} fillOpacity={0.85} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-3 p-4 bg-amber-50 rounded-lg border border-amber-200">
          <p className="text-sm text-amber-900">
            <span className="font-bold">Engaged players (31–100 rounds) lose the most: −2.18pp.</span> This is the highest-LTV segment — players actively progressing and most likely to convert. The aggregate −0.82pp undersells the real cost.
          </p>
        </div>
      </Card>

      {/* Why it matters */}
      <Card className="border-2 border-blue-200 bg-blue-50">
        <div className="text-xs font-bold uppercase tracking-wider text-blue-700 mb-2">Why this matters</div>
        <p className="text-base text-blue-900 leading-relaxed">{cc.insight}</p>
      </Card>
    </div>
  );
};

// ============================================================================
// TAB 4: EXPERIMENT DESIGNER
// ============================================================================
const ExperimentDesigner = () => {
  const [baseline, setBaseline] = useState(15);
  const [mde, setMde] = useState(5);
  const [alpha, setAlpha] = useState(5);
  const [power, setPower] = useState(80);
  const [dailyTraffic, setDailyTraffic] = useState(5000);
  const [arpu, setArpu] = useState(50);

  // Sample size calculation (two-proportion z-test)
  const calculateSampleSize = () => {
    const p1 = baseline / 100;
    const p2 = p1 * (1 + mde / 100);
    const pBar = (p1 + p2) / 2;
    const zAlpha = alpha === 5 ? 1.96 : 2.576; // 5% or 1%
    const zBeta = power === 80 ? 0.84 : power === 90 ? 1.28 : 1.645;
    const numerator = zAlpha * Math.sqrt(2 * pBar * (1 - pBar)) + zBeta * Math.sqrt(p1 * (1 - p1) + p2 * (1 - p2));
    const denominator = p2 - p1;
    const n = Math.pow(numerator / denominator, 2);
    return Math.ceil(n);
  };

  const sampleSize = calculateSampleSize();
  const totalSample = sampleSize * 2;
  const durationDays = Math.ceil(totalSample / dailyTraffic);
  const expectedAbsoluteLift = (baseline / 100) * (mde / 100);
  const expectedAnnualValue = totalSample * expectedAbsoluteLift * arpu * (365 / Math.max(durationDays, 14));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Experiment Designer</h2>
        <p className="text-sm text-gray-500 mt-1">
          Sample size + duration + business case in one place. Most calculators stop at sample size.
          This one tells you whether the test is worth running.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Inputs */}
        <Card>
          <SectionTitle>Statistical Parameters</SectionTitle>
          <div className="space-y-5">
            <div>
              <label className="text-xs font-medium text-gray-600 flex justify-between mb-2">
                <span>Baseline conversion rate</span>
                <span className="font-bold text-gray-900">{baseline}%</span>
              </label>
              <input type="range" min="1" max="50" step="0.5" value={baseline}
                onChange={e => setBaseline(parseFloat(e.target.value))}
                className="w-full" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 flex justify-between mb-2">
                <span>Minimum detectable effect (relative)</span>
                <span className="font-bold text-gray-900">{mde}%</span>
              </label>
              <input type="range" min="1" max="30" step="0.5" value={mde}
                onChange={e => setMde(parseFloat(e.target.value))}
                className="w-full" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 flex justify-between mb-2">
                <span>Significance level (α)</span>
                <span className="font-bold text-gray-900">{alpha}%</span>
              </label>
              <div className="flex gap-2">
                {[1, 5].map(a => (
                  <button key={a} onClick={() => setAlpha(a)}
                    className={`flex-1 py-2 text-xs font-medium rounded ${
                      alpha === a ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600"
                    }`}>
                    {a}%
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 flex justify-between mb-2">
                <span>Statistical power</span>
                <span className="font-bold text-gray-900">{power}%</span>
              </label>
              <div className="flex gap-2">
                {[80, 90, 95].map(p => (
                  <button key={p} onClick={() => setPower(p)}
                    className={`flex-1 py-2 text-xs font-medium rounded ${
                      power === p ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-600"
                    }`}>
                    {p}%
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <SectionTitle>Business Parameters</SectionTitle>
          <div className="space-y-5">
            <div>
              <label className="text-xs font-medium text-gray-600 flex justify-between mb-2">
                <span>Daily eligible traffic</span>
                <span className="font-bold text-gray-900">{dailyTraffic.toLocaleString()}</span>
              </label>
              <input type="range" min="500" max="50000" step="500" value={dailyTraffic}
                onChange={e => setDailyTraffic(parseInt(e.target.value))}
                className="w-full" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 flex justify-between mb-2">
                <span>ARPU per converted user ($)</span>
                <span className="font-bold text-gray-900">${arpu}</span>
              </label>
              <input type="range" min="10" max="500" step="10" value={arpu}
                onChange={e => setArpu(parseInt(e.target.value))}
                className="w-full" />
            </div>
          </div>
        </Card>
      </div>

      {/* Outputs */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Users per Variant" value={sampleSize.toLocaleString()} color={COLORS.primary} />
        <StatCard label="Total Users Needed" value={totalSample.toLocaleString()} />
        <StatCard label="Estimated Duration"
          value={`${durationDays}d`}
          sub={durationDays < 14 ? "⚠ extend to 14d minimum" : durationDays > 56 ? "⚠ over 8 weeks" : "✓ healthy duration"}
          color={durationDays < 14 || durationDays > 56 ? COLORS.warning : COLORS.positive} />
        <StatCard label="Annualized Business Value"
          value={`$${Math.round(expectedAnnualValue / 1000)}K`}
          sub="if effect detected & shipped"
          color={COLORS.positive} />
      </div>

      {/* Decision matrix */}
      <Card>
        <SectionTitle>Should You Run This Test?</SectionTitle>
        <div className="space-y-3 mt-3">
          <DecisionRow
            check={mde >= 3}
            text="MDE is realistic for the feature type"
            detail={mde < 3 ? "Very small MDE — needs huge sample size" : "MDE in reasonable range for most product changes"}
          />
          <DecisionRow
            check={durationDays >= 14 && durationDays <= 56}
            text="Duration is healthy (2-8 weeks)"
            detail={durationDays < 14 ? "Too short — increase MDE or wait for more traffic" : durationDays > 56 ? "Too long — risk of seasonality contamination" : "Good duration window"}
          />
          <DecisionRow
            check={expectedAnnualValue > 50000}
            text="Annualized value exceeds opportunity cost (~$50K)"
            detail={expectedAnnualValue < 50000 ? "Low ROI — consider a higher-impact test instead" : "Strong business case for running this test"}
          />
        </div>

        <div className="mt-5 p-4 rounded-lg border-2"
          style={{
            backgroundColor: durationDays >= 14 && durationDays <= 56 && mde >= 3 && expectedAnnualValue > 50000 ? "#ECFDF5" : "#FEF3C7",
            borderColor: durationDays >= 14 && durationDays <= 56 && mde >= 3 && expectedAnnualValue > 50000 ? "#10B981" : "#F59E0B",
          }}>
          <div className="text-xs font-bold uppercase tracking-wider mb-1"
            style={{ color: durationDays >= 14 && durationDays <= 56 && mde >= 3 && expectedAnnualValue > 50000 ? "#065F46" : "#92400E" }}>
            Recommendation
          </div>
          <p className="text-sm font-medium"
            style={{ color: durationDays >= 14 && durationDays <= 56 && mde >= 3 && expectedAnnualValue > 50000 ? "#065F46" : "#92400E" }}>
            {durationDays >= 14 && durationDays <= 56 && mde >= 3 && expectedAnnualValue > 50000
              ? "✓ This test design is sound. Proceed with launch."
              : "⚠ Adjust parameters before running. Consider a higher MDE, more traffic, or a different test."}
          </p>
        </div>
      </Card>
    </div>
  );
};

const DecisionRow = ({ check, text, detail }) => (
  <div className={`flex items-start gap-3 p-3 rounded-lg ${check ? "bg-green-50" : "bg-amber-50"}`}>
    <div className="flex-shrink-0 mt-0.5 text-lg">{check ? "✓" : "⚠"}</div>
    <div>
      <div className={`text-sm font-medium ${check ? "text-green-900" : "text-amber-900"}`}>{text}</div>
      <div className={`text-xs mt-0.5 ${check ? "text-green-700" : "text-amber-700"}`}>{detail}</div>
    </div>
  </div>
);

// ============================================================================
// TAB 5: TRUST & GOVERNANCE
// ============================================================================
const Governance = () => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900">Trust & Governance Framework</h2>
      <p className="text-sm text-gray-500 mt-1">
        How a mature experimentation program operates — beyond running individual tests.
      </p>
    </div>

    {/* Pre-test gates */}
    <Card>
      <SectionTitle>Pre-Test Gates (Before Launch)</SectionTitle>
      <div className="space-y-3">
        <GateRow num="1" title="Hypothesis is falsifiable"
          desc="The test must have a clear definition of what 'wrong' looks like. 'See if it helps' is not falsifiable." />
        <GateRow num="2" title="Primary metric is pre-specified"
          desc="One primary metric, declared before launch. No metric shopping after results come in." />
        <GateRow num="3" title="Guardrail metrics include D7 + D30 retention"
          desc="Activation/engagement tests must monitor long-term metrics, not just immediate behavior change." />
        <GateRow num="4" title="MDE is anchored to historical effect sizes"
          desc="Default MDE: 3% for engagement features, 5% for activation, 10% for monetization. Override with rationale." />
        <GateRow num="5" title="Duration ≥ 2 weeks (3 weeks for behavior-change tests)"
          desc="Captures weekly seasonality. Behavior-change tests need 3+ weeks to filter out novelty effects." />
        <GateRow num="6" title="Concurrent test conflict check"
          desc="Identify other live tests on the same population. Document expected interaction or randomize across tests." />
      </div>
    </Card>

    {/* During-test monitoring */}
    <Card>
      <SectionTitle>During-Test Monitoring</SectionTitle>
      <div className="space-y-3">
        <GateRow num="1" title="Daily SRM check"
          desc="Sample Ratio Mismatch indicates randomization failure or instrumentation bug. Test fails immediately if SRM detected." />
        <GateRow num="2" title="Guardrail metric alerting"
          desc="If any guardrail moves &gt;10% in unexpected direction, pause for review." />
        <GateRow num="3" title="No peeking at primary metric"
          desc="Decision is made at pre-specified end date. No early stopping on the primary metric without sequential testing methodology." />
      </div>
    </Card>

    {/* Post-test rules */}
    <Card>
      <SectionTitle>Post-Test Decision Rules</SectionTitle>
      <div className="space-y-3">
        <GateRow num="1" title="Significance + business value threshold"
          desc="Statistical significance is necessary but not sufficient. Effect size must exceed minimum practical threshold (varies by metric)." />
        <GateRow num="2" title="Guardrail metrics override primary metric"
          desc="A primary metric win with a guardrail loss defaults to NO SHIP. Requires affirmative override decision." />
        <GateRow num="3" title="Segment analysis required for null results"
          desc="If overall effect is null/flat, mandatory segment analysis to check for opposing effects (Simpson's paradox)." />
        <GateRow num="4" title="Holdout for major features"
          desc="Any feature affecting &gt;500K MAU requires a permanent 5-10% holdout for ongoing measurement." />
      </div>
    </Card>

    {/* Anti-patterns */}
    <Card className="border-2 border-red-200 bg-red-50">
      <div className="text-xs font-bold uppercase tracking-wider text-red-700 mb-3">
        Anti-Patterns We Don't Allow
      </div>
      <ul className="space-y-2 text-sm text-red-900">
        <li>• Running a test "to see what happens" without a hypothesis</li>
        <li>• Stopping a test early because the result is "going in the right direction"</li>
        <li>• Re-defining the primary metric after seeing results</li>
        <li>• Shipping based on per-segment significance after non-significant overall (multiple testing)</li>
        <li>• Running on a population also exposed to another live test without interaction analysis</li>
        <li>• Treating non-significant p-values as proof of "no effect"</li>
      </ul>
    </Card>
  </div>
);

const GateRow = ({ num, title, desc }) => (
  <div className="flex items-start gap-4 p-3 bg-gray-50 rounded-lg">
    <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gray-900 text-white flex items-center justify-center text-xs font-bold">
      {num}
    </div>
    <div>
      <div className="font-medium text-sm text-gray-900">{title}</div>
      <div className="text-xs text-gray-600 mt-0.5">{desc}</div>
    </div>
  </div>
);

// ============================================================================
// TAB 6: EXECUTIVE BRIEFING
// ============================================================================
const ExecutiveBriefing = () => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold text-gray-900">Executive Briefing</h2>
      <p className="text-sm text-gray-500 mt-1">
        One-page summary for VP of Growth — Q3 2025
      </p>
    </div>

    {/* TL;DR */}
    <div className="rounded-xl p-6 bg-gradient-to-br from-blue-600 to-blue-800 text-white">
      <div className="text-xs font-bold uppercase tracking-wider opacity-80 mb-2">TL;DR</div>
      <p className="text-lg leading-relaxed">
        We ran 6 experiments this quarter. <span className="font-bold">2 shipped. 1 shipped to a specific segment. 2 killed. 1 needs re-running.</span> The 4 that didn't ship are arguably more valuable than the 2 that did — they revealed systematic gaps in how we design and read experiments.
      </p>
    </div>

    {/* Key wins */}
    <div className="grid grid-cols-2 gap-6">
      <Card>
        <SectionTitle className="text-green-700">What Shipped</SectionTitle>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
            <span className="text-lg">✓</span>
            <div>
              <div className="font-medium text-sm text-green-900">E1: Social Login</div>
              <div className="text-xs text-green-700 mt-0.5">+9.2% signup completion. Estimated +28K monthly signups.</div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
            <span className="text-lg">✓</span>
            <div>
              <div className="font-medium text-sm text-green-900">E6: Leaderboard Gamification</div>
              <div className="text-xs text-green-700 mt-0.5">+22% DAU. Projected $10.7M annual revenue impact.</div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-emerald-50 rounded-lg">
            <span className="text-lg">✓</span>
            <div>
              <div className="font-medium text-sm text-emerald-900">E2: Extended Trial (new users only)</div>
              <div className="text-xs text-emerald-700 mt-0.5">+22.9% conversion for new users. ~$216K annual.</div>
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <SectionTitle className="text-red-700">What We Didn't Ship (and Why It Matters)</SectionTitle>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
            <span className="text-lg">✕</span>
            <div>
              <div className="font-medium text-sm text-red-900">E4: Shorter Onboarding</div>
              <div className="text-xs text-red-700 mt-0.5">Would have damaged D30 retention by 9.5%, costing $697K/year.</div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
            <span className="text-lg">✕</span>
            <div>
              <div className="font-medium text-sm text-red-900">E3: Push Time Shift</div>
              <div className="text-xs text-red-700 mt-0.5">Looked like a +14% win for the first week. True effect is +2%.</div>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
            <span className="text-lg">↻</span>
            <div>
              <div className="font-medium text-sm text-amber-900">E5: AI Conversation Practice</div>
              <div className="text-xs text-amber-700 mt-0.5">Test was undersized. Re-running with proper power before decision.</div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    {/* What we need from leadership */}
    <Card>
      <SectionTitle>What the Program Needs From Leadership</SectionTitle>
      <div className="space-y-3 mt-3">
        <div className="flex items-start gap-3">
          <div className="w-1 h-12 bg-blue-500 rounded-full flex-shrink-0" />
          <div>
            <div className="font-medium text-sm text-gray-900">Patience for 3-week minimum test durations</div>
            <div className="text-xs text-gray-600 mt-0.5">PMs feel pressure to ship fast. Two of the four "failed" tests this quarter would have shipped on a 1-week timeline. The cost of slow tests is much lower than the cost of bad ships.</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="w-1 h-12 bg-blue-500 rounded-full flex-shrink-0" />
          <div>
            <div className="font-medium text-sm text-gray-900">Commitment to D30 retention as a guardrail</div>
            <div className="text-xs text-gray-600 mt-0.5">E4 is the case for this. We need executive air cover when D1 metrics look great but D30 doesn't.</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="w-1 h-12 bg-blue-500 rounded-full flex-shrink-0" />
          <div>
            <div className="font-medium text-sm text-gray-900">Investment in test instrumentation for new product surfaces</div>
            <div className="text-xs text-gray-600 mt-0.5">3 high-priority Q4 features can't be properly tested without additional event tracking. Estimated investment: 2 engineering weeks.</div>
          </div>
        </div>
      </div>
    </Card>

    {/* What's next */}
    <Card>
      <SectionTitle>Q4 Priorities</SectionTitle>
      <div className="grid grid-cols-3 gap-4 mt-3">
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Run</div>
          <div className="text-sm font-medium text-gray-900 mt-2">Re-run E5 (AI Practice) with proper sample size</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Build</div>
          <div className="text-sm font-medium text-gray-900 mt-2">Standardize segment analysis in our experimentation tool</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Codify</div>
          <div className="text-sm font-medium text-gray-900 mt-2">Publish experimentation playbook based on Q3 patterns</div>
        </div>
      </div>
    </Card>
  </div>
);

// ============================================================================
// MAIN APP
// ============================================================================
function App() {
  const [tab, setTab] = useState("program");
  const [selectedExp, setSelectedExp] = useState("E1");

  const tabs = [
    { id: "program", label: "Program Dashboard", icon: "📊" },
    { id: "gallery", label: "Experiment Gallery", icon: "🔬" },
    { id: "cookiecats", label: "Cookie Cats Deep Dive", icon: "🎮" },
    { id: "designer", label: "Experiment Designer", icon: "🛠️" },
    { id: "governance", label: "Trust & Governance", icon: "🛡️" },
    { id: "executive", label: "Executive Briefing", icon: "📋" },
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#F8FAFC" }}>
      {/* Header */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Experimentation Playbook · Q3 2025 Quarterly Review
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1.5">6 A/B Tests, 2 Ships: An Experimentation Program Review</h1>
            </div>
            <div className="text-right">
              <div className="text-xs uppercase tracking-wider text-gray-400">Author</div>
              <div className="text-sm font-medium text-gray-700">Freena Wang</div>
            </div>
          </div>

          {/* Tab navigation */}
          <div className="flex gap-1 mt-5 -mb-5 overflow-x-auto">
            {tabs.map(t => (
              <button key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap ${
                  tab === t.id
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-900"
                }`}>
                <span className="mr-2">{t.icon}</span>
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {tab === "program" && <ProgramDashboard onSelectExperiment={(id) => { setSelectedExp(id); setTab("gallery"); }} />}
        {tab === "gallery" && <ExperimentGallery selectedId={selectedExp} onSelect={setSelectedExp} />}
        {tab === "cookiecats" && <CookieCatsDeepDive />}
        {tab === "designer" && <ExperimentDesigner />}
        {tab === "governance" && <Governance />}
        {tab === "executive" && <ExecutiveBriefing />}
      </div>

      {/* Footer */}
      <div className="border-t border-slate-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-gray-400 text-center">
          Experimentation Playbook · Q3 2025 Quarterly Review · Built by{" "}
          <a href="https://www.linkedin.com/in/freena-wang/" target="_blank" rel="noopener noreferrer"
            className="text-blue-500 hover:text-blue-700 underline">Freena Wang</a>
        </div>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
