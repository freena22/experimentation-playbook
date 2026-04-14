# 6 A/B Tests, 2 Ships: An Experimentation Program Review

> *How I would run, read, and learn from a quarter of experiments at a consumer SaaS company.*

**Live Dashboard:** [View on GitHub Pages →](https://freena22.github.io/experimentation-playbook/)

---

## Why This Project

Most A/B testing portfolios show one thing: *"I can analyze a single experiment correctly."*

That's table stakes. The harder — and more valuable — question is: **how does an organization run dozens of experiments a year without stepping on itself, learn from what doesn't ship, and avoid the traps that turn surface wins into long-term losses?**

This project answers that question. It shows how I would lead the experimentation function at a consumer SaaS company — not just as an analyst running tests, but as a partner helping the organization decide *which tests matter, how to read them honestly, and what to do with results that don't fit a clean narrative.*

---

## What This Project Is (And Isn't)

**This is not an A/B test analysis project. It's a design for how an analytics function should operate an experimentation program at scale** — covering governance, analytical rigor, stakeholder communication, and decision-quality frameworks.

### What it is

- A **framework** for running experimentation as an ongoing program, not a series of one-off tests
- A **portfolio** of 6 experiments chosen to illustrate the recurring patterns a real growth team encounters (Simpson's paradox, novelty decay, underpowered tests, primary vs. north star metric conflicts)
- An **operating model** with pre-test gates, during-test monitoring, post-test decision rules, and anti-patterns — the kind of playbook a mature experimentation function runs on
- A **reusable toolset** (Experiment Designer, Governance Framework, per-experiment analysis template) that's scalable across many tests, not hand-crafted for each

### What it is not

- **Not a single A/B test analysis.** That's table stakes; this project assumes the reader already expects that skill and shows the layer above it.
- **Not a production experimentation platform.** Platforms handle assignment services, feature flags, streaming pipelines, and access control — that's Engineering work. This project shows the analytical and governance layer that operates *on top of* a platform.
- **Not a demonstration of handling real-world data-layer problems** (instrumentation bugs, SRM root-cause investigation, cross-platform event schema issues, bot filtering). Those consume ~80% of the real experimentation workflow, but they're best demonstrated through production work history, not portfolio simulations. My years at Walmart Connect and Google Play involved exactly this kind of data-reliability work — here I'm deliberately focusing on the judgment layer, which is the hardest to demonstrate through code and the most differentiating at senior levels.

### The core capability being demonstrated

When a PM says *"We got +12%, can we ship?"*, the most valuable person in the room is the one who asks:

- *What does the D30 retention look like?*
- *Did we check SRM?*
- *Is this a new-user effect or across all segments?*
- *Was this running concurrent with another test?*

That capability — being the calm, rigorous voice in a fast-moving growth team — is what this project is built to show.

---

## Context: LinguaLeap Q3 2025

**LinguaLeap** is a simulated freemium language learning app (~2M MAU, Duolingo-style business model) used as the backdrop for this project. The portfolio reflects what a realistic quarter at a growth-stage consumer SaaS company might produce: 6 experiments across acquisition, activation, engagement, and monetization.

The analysis here is the **quarterly experimentation review** I would deliver to the VP of Growth — covering not just results, but what the program itself is teaching us.

---

## The Quarter in One Chart

| # | Experiment | Area | Raw Read | Decision | Why |
|---|-----------|------|----------|----------|-----|
| E1 | Social login at signup | Acquisition | +9.2% signup completion, p<0.001 | ✅ Ship | Clean result, consistent across segments |
| E2 | Extended trial (7 → 14 days) | Monetization | Flat overall (p=0.09) | ✅ Ship to new users only | Hidden heterogeneity: +22.9% new / -8% tenured |
| E3 | Push notification time shift | Engagement | +15% week 1, +2% week 4 | ❌ Kill | Novelty effect; long-term incremental near zero |
| E4 | Shortened onboarding (5 → 3 steps) | Activation | +12% D1 activation, p<0.001 | ❌ Kill | D7 retention +1.3%, D30 retention -9.5% |
| E5 | AI conversation practice | Engagement | +2.6% engagement, p=0.13 | 🔁 Re-run | Underpowered test, not a null result |
| E6 | Leaderboard gamification | Engagement | +22% DAU, p<0.001 | ✅ Ship | Clean result validated via holdout |

**Ship rate: 33% (2 unconditional ships + 1 segment-level ship, out of 6 experiments).**

A team shipping 80%+ of experiments isn't experimenting — they're rubber-stamping. A team shipping under 10% is over-investing in low-impact tests. 33% is the kind of rate a mature program sustains over time.

---

## What This Project Demonstrates

### Level 1 — Single experiment analysis, done right

Every experiment in this portfolio is analyzed with:

- **Pre-test**: Sample size & MDE calculation, SRM check, concurrent test conflict review
- **In-test**: Guardrail metric monitoring (no peeking on primary)
- **Post-test**: Primary metric significance testing (frequentist + Bayesian), variance reduction via CUPED where applicable, segment-level analysis, guardrail metric review

Standard stuff. Necessary but not sufficient.

### Level 2 — Segment-aware decision making

Three of the six experiments changed decision after segment analysis:

- **E2** looked flat overall — but new users loved it (+22.9%) and tenured users hated it (-8%). Shipping to everyone would have been a wash; shipping to new users only is a clear win.
- **E4** had the strongest primary metric signal in the portfolio (+12% D1 activation) but killed long-term retention. Primary metric wins can mask North Star losses.
- **E3**'s weekly decomposition revealed the time-shift effect was concentrated in weeks 1–2 and reverted by week 4 — classic novelty.

**The job isn't to measure the average effect. It's to find where the effect lives.**

### Level 3 — Program-level thinking

The real output of this quarter isn't the ship decisions. It's the **pattern** across tests:

- **Two out of six** (E3, E4) would have degraded long-term health if shipped on primary metric alone → *policy: activation/engagement tests must validate against D30 retention before ship*
- **One of six** (E2) required segment analysis to find the right answer → *segment analysis shouldn't be optional; it should be standard*
- **One of six** (E5) was under-designed → *MDE discipline at test design stage needs tightening*

These aren't post-hoc observations. They're the *inputs to next quarter's experimentation policy.* That's what makes it a program, not a series of tests.

### Level 4 — Decision-ready communication

Every experiment has a one-page brief answering three questions a VP actually cares about:

1. **What did we learn?** (not "what did the p-value say")
2. **What should we do?** (with confidence level)
3. **What would change our minds?** (the falsifiable conditions for reversing the decision)

---

## Dashboard Structure

**1. Program Dashboard** — Quarter-level view: 6 experiments, ship/kill/re-run breakdown, cumulative impact, cross-experiment learnings.

**2. Experiment Gallery** — Per-experiment deep dive: hypothesis, design, raw results, deeper analysis, decision, and learnings — structured identically for each so patterns across tests become visible.

**3. Cookie Cats Deep Dive** — A standalone analysis of the classic Cookie Cats mobile game gate experiment (~90K users, reproduced from public benchmark). Shows hands-on analytical depth on real data: retention curves, statistical testing, bootstrap confidence intervals, Bayesian posterior analysis, and segment-level uplift.

**4. Experiment Designer** — Interactive tool for sizing a new test: sample size, MDE, duration estimator, and — critically — a "business case" layer that translates statistical parameters into expected business value. *Most calculators tell you how many users you need. This one also tells you whether the test is worth running.*

**5. Trust & Governance Framework** — The operating model behind the program: pre-test gates, during-test monitoring, post-test decision rules, and a list of anti-patterns we don't allow.

**6. Executive Briefing** — The one-page version for the VP of Growth: what we shipped, what we learned, what we're investing in next quarter, and what the program needs from leadership.

---

## Technical Approach

The technical stack is **intentionally appropriate, not intentionally complex**. Every method used is justified by the analytical question, not chosen to show range.

**Statistical methods:**

- Frequentist hypothesis testing (two-proportion z-test, Welch's t-test)
- Bayesian A/B analysis (Beta-Binomial conjugate) — paired with frequentist results, not replacing them
- CUPED variance reduction (applied selectively, only where pre-period data is meaningful)
- Bootstrap confidence intervals (for non-parametric robustness checks on continuous metrics)
- Segment-level analysis with attention to multiple comparisons
- Post-hoc power analysis (for diagnosing underpowered tests)

**Diagnostics:**

- SRM (Sample Ratio Mismatch) check on every test
- Guardrail metric monitoring
- Concurrent test interaction audit
- Holdout validation for major features

### What I Deliberately Did Not Do

- **No causal forests / uplift models** — the HTE analysis here is segment-based and interpretable, which is what a growth team can actually action
- **No sequential testing / mSPRT** — interesting academically but overkill for 2–4 week tests
- **No ML-based heterogeneity estimation** — the business doesn't need a black box; it needs a defensible recommendation
- **No full experimentation platform engineering** — randomization services, feature flags, streaming analytics are platform/infra work, not analytics work

*The signal of analytical maturity isn't using every tool you know — it's knowing which tool the situation calls for.*

---

## Project Structure

```
experimentation-playbook/
├── model/
│   ├── generate_experiment_data.py   # Simulates 6 experiments + reproduces Cookie Cats
│   ├── analyze_experiments.py        # Runs the full analysis suite
│   └── cookie_cats_analysis.py       # Dedicated deep-dive on the real-data case
├── dashboard/
│   └── experimentation_dashboard.jsx # Interactive React dashboard (6 tabs)
├── data/
│   ├── experiments/                  # Generated CSVs (one per experiment)
│   └── results/                      # Analysis output JSONs
├── charts/                           # Static PNG charts (one per experiment + Cookie Cats)
├── docs/                             # GitHub Pages: index.html + experimentation_dashboard.jsx (CDN React/Recharts + Babel)
├── methodology.md                    # Technical methodology deep-dive
├── requirements.txt
└── README.md
```

**Key files:**

- [`model/generate_experiment_data.py`](./model/generate_experiment_data.py) — Data generation with ground-truth effects and embedded teaching moments
- [`model/analyze_experiments.py`](./model/analyze_experiments.py) — Analysis pipeline with methods tailored per experiment
- [`methodology.md`](./methodology.md) — Full statistical methodology

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Generate data (one-time)
python model/generate_experiment_data.py

# Run full analysis
python model/analyze_experiments.py
python model/cookie_cats_analysis.py

# Generate charts
python model/generate_charts.py
python model/cookie_cats_charts.py
```

The React dashboard is a single `.jsx` file that can be rendered in any React environment. Dependencies: `react`, `recharts`.

---

## Caveats & Honest Limitations

- **The 6 experiments are simulated**, with ground-truth effects set during data generation. This is for methodology demonstration — in production, you don't know the ground truth, which makes experimentation much harder and judgment much more valuable.
- **Cookie Cats data is reproduced** from the public benchmark dataset using its published distributional characteristics (sample size, retention rates, gamerounds distribution). It's being used as a "deep dive on real messy data" case study, not as proof of broader analytical scale.
- **Segment definitions are predefined** in the simulation. In reality, finding the right segments is half the battle, and doing it post-hoc raises multiple-testing concerns. The segments here are chosen for clarity of teaching, not optimized via search.
- **No causal inference beyond experimentation** — quasi-experimental methods (DiD, synthetic control, RDD) for cases where experimentation isn't feasible are important in practice but out of scope here.
- **This is one quarter's worth of experiments.** Real program maturity takes years of accumulated learnings. What's shown here is what quarter 4 or 5 of an experimentation program might look like, not year 1.

---

## How to Use This Project

If you're evaluating **analytical skill**: see the [Cookie Cats Deep Dive](https://freena22.github.io/experimentation-playbook/) and the E2 / E4 / E5 experiment analyses.

If you're evaluating **framework thinking**: see the [Program Dashboard](https://freena22.github.io/experimentation-playbook/) and [Trust & Governance Framework](https://freena22.github.io/experimentation-playbook/).

If you're evaluating **stakeholder communication**: see the [Executive Briefing](https://freena22.github.io/experimentation-playbook/) and any per-experiment one-pager in the Gallery.

---

## Author

**Freena Wang** — Senior Marketing & Product Analytics Professional

Built as a portfolio project demonstrating end-to-end experimentation program capabilities: from designing individual tests through program-level governance and executive communication.

Companion project to [ShopNova Marketing Mix Model](https://freena22.github.io/marketing-mix-model/), which covers the aggregate-measurement side of growth analytics.

Together, the two projects span the full growth measurement stack: **MMM answers "where should marketing invest?", experimentation answers "what should product change?"**
