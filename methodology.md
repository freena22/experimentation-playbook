# Methodology

This document describes the statistical methods used in the LinguaLeap experimentation analysis. Each method was chosen for a specific analytical question, not to demonstrate range.

---

## Table of Contents

1. [Data Generation Philosophy](#1-data-generation-philosophy)
2. [Sample Ratio Mismatch (SRM) Check](#2-sample-ratio-mismatch-srm-check)
3. [Frequentist Hypothesis Testing](#3-frequentist-hypothesis-testing)
4. [Bayesian A/B Analysis](#4-bayesian-ab-analysis)
5. [CUPED Variance Reduction](#5-cuped-variance-reduction)
6. [Bootstrap Confidence Intervals](#6-bootstrap-confidence-intervals)
7. [Power Analysis](#7-power-analysis)
8. [Segment Analysis & Simpson's Paradox](#8-segment-analysis--simpsons-paradox)
9. [Novelty Effect Detection](#9-novelty-effect-detection)
10. [Holdout Validation](#10-holdout-validation)
11. [Business Impact Modeling](#11-business-impact-modeling)

---

## 1. Data Generation Philosophy

The six experiments are simulated with deliberate ground-truth effects. Each was designed to illuminate a specific analytical pattern:

| Experiment | Ground-truth design |
|-----------|---------------------|
| E1 | Uniform +9% lift across all segments (clean winner) |
| E2 | +18% for new users, -10% for tenured, weighted to produce near-flat overall |
| E3 | +15% lift in week 1 decaying exponentially to +2% steady state |
| E4 | +12% on D1 activation but -8% conditional decay in D7/D30 retention |
| E5 | Real +2% effect with sample size sized for 8% MDE (deliberately underpowered) |
| E6 | +22% lift with CUPED-eligible pre-period covariate |

Cookie Cats data is reproduced from the published dataset characteristics (n=90,189; retention_1 ≈ 44.8/44.2%; retention_7 ≈ 19.0/18.2%; right-skewed gamerounds with max ~1,000+).

**Why simulation works for methodology demonstration but has limits:**
- ✓ Lets us show that analysis recovers known effects
- ✓ Demonstrates the full analytical pipeline
- ✗ Doesn't capture real-world instrumentation issues, unknown confounders, or true uncertainty
- ✗ Segment definitions are predefined, not discovered

---

## 2. Sample Ratio Mismatch (SRM) Check

**Purpose:** Detect broken randomization before analyzing outcomes.

**Method:** Pearson's χ² test on observed vs. expected variant allocation.

$$\chi^2 = \sum_{i} \frac{(O_i - E_i)^2}{E_i}$$

with 1 degree of freedom for a two-arm test.

**Threshold:** We fail the test at p < 0.001 (not 0.05). SRM is a severity check, and false positives here are more costly than false negatives. A p-value of 0.04 with 100K users in each arm can reflect trivial imbalance; a p-value of 0.0005 almost always reflects an instrumentation problem.

**Applied to:** All 6 LinguaLeap experiments + Cookie Cats. All passed.

**What we'd do on failure:** Halt analysis immediately. Investigate randomization service, sample selection logic, and any filters applied post-assignment. Do not analyze outcomes until cause is identified and remediated.

---

## 3. Frequentist Hypothesis Testing

### 3.1 Two-proportion z-test (binary outcomes)

Used for: E1, E2, E4, Cookie Cats retention.

$$z = \frac{\hat{p}_T - \hat{p}_C}{\sqrt{\hat{p}(1-\hat{p})\left(\frac{1}{n_T} + \frac{1}{n_C}\right)}}$$

where $\hat{p} = \frac{x_T + x_C}{n_T + n_C}$ is the pooled estimate under H₀.

**95% CI on absolute difference:**
$$\hat{p}_T - \hat{p}_C \pm 1.96 \sqrt{\frac{\hat{p}_T(1-\hat{p}_T)}{n_T} + \frac{\hat{p}_C(1-\hat{p}_C)}{n_C}}$$

Note: The pooled SE is used for the test statistic (assumes H₀); unpooled SE is used for the CI (uses observed rates). This is the standard practice.

### 3.2 Welch's t-test (continuous outcomes)

Used for: E3 (daily push opens), E5 (sessions), E6 (active days).

Welch's version is preferred over Student's t-test because it doesn't assume equal variances between groups — a safer default for real-world A/B tests where treatments can shift variance as well as means.

### 3.3 What we did NOT use

- **Mann-Whitney U test:** Considered for E6 where sessions are right-skewed, but the sample sizes (n > 25K per arm) make the CLT apply comfortably. Welch's t-test is appropriate.
- **Sequential testing (mSPRT, Pocock boundaries):** Our tests are fixed-horizon 2–4 weeks. Sequential methods are valuable when peeking is operationally necessary; they're not worth the complexity when you can commit to a duration.

---

## 4. Bayesian A/B Analysis

**Purpose:** Report probability statements that stakeholders can actually reason about.

### 4.1 Beta-Binomial conjugate (binary outcomes)

For a conversion rate with uniform prior Beta(1, 1):

$$p_T \sim \text{Beta}(1 + x_T, 1 + n_T - x_T)$$
$$p_C \sim \text{Beta}(1 + x_C, 1 + n_C - x_C)$$

We sample 50,000 draws from each posterior and compute:

- **P(Treatment > Control):** Fraction of draws where $p_T > p_C$
- **Expected lift distribution:** Full posterior of $(p_T - p_C)/p_C$
- **P(lift > X%):** For any threshold of business interest

**Why this matters:** Business decisions are about probability, not p-values. Saying "there's a 99.86% chance gate_30 retains better than gate_40" is more useful to a VP than "p = 0.003."

### 4.2 Continuous outcomes

For continuous metrics (E5, E6), we approximate the posterior as Normal with mean = sample mean and standard error = sample SE (non-informative prior on the mean, assuming large samples). This is a standard large-sample approximation that avoids the need for a conjugate prior on variance.

### 4.3 Choice of prior

We use uniform Beta(1, 1) priors throughout. In a real program with historical baselines:

- For well-understood metrics (e.g., signup completion), an informative prior centered near the historical baseline reduces shrinkage noise
- For novel features with no baseline, uniform priors avoid introducing bias

For a methodology demo, uniform priors let results speak for themselves.

---

## 5. CUPED Variance Reduction

**Applied to:** E6 (Leaderboard experiment).

**CUPED** (Controlled experiments Using Pre-Experiment Data) reduces variance by using a pre-period covariate to explain away user-level baseline variation:

$$Y_{\text{adj}} = Y - \theta (X - \mathbb{E}[X])$$

where $\theta = \frac{\text{Cov}(X, Y)}{\text{Var}(X)}$ is computed on the pooled data.

**Key property:** $\mathbb{E}[Y_{\text{adj}}] = \mathbb{E}[Y]$, so the point estimate is unchanged. But $\text{Var}(Y_{\text{adj}}) = \text{Var}(Y)(1 - \rho^2)$, where $\rho$ is the correlation between pre-period and in-experiment metrics.

**In E6:** Pre-period sessions correlated r ≈ 0.48 with in-experiment active days. CUPED reduced the variance of the treatment effect estimate by 23.3% — equivalent to running with ~30% more users.

**When CUPED is worth using:**
- ✓ Pre-experiment metric data is reliably available
- ✓ The metric is stable (past behavior predicts future behavior)
- ✓ Sample size is a binding constraint

**When to skip CUPED:**
- ✗ Pre-period data is sparse or unreliable
- ✗ Short-horizon tests where pre-period isn't meaningful
- ✗ Outcome is fundamentally new (no predictive baseline exists)

### What CUPED is NOT

CUPED does not make a non-significant test significant by magic. It reduces variance by using information already present in the data. If the treatment effect is zero, CUPED will correctly estimate zero with tighter confidence intervals around zero.

---

## 6. Bootstrap Confidence Intervals

**Applied to:** Cookie Cats retention differences (as a robustness check).

**Method:** Non-parametric percentile bootstrap with 5,000 iterations. Resample each variant with replacement to sample size n, compute the statistic on each resample, take the 2.5th and 97.5th percentiles as the CI.

**Why both z-test CI and bootstrap CI?**

The z-test CI is analytical (fast, based on asymptotic theory). The bootstrap CI is empirical (slower but makes fewer assumptions).

When they agree — as they did for Cookie Cats (1-day diff CI: z-test [−0.92, +0.39], bootstrap [−0.92, +0.38]) — we have high confidence the inference is robust to distributional assumptions.

When they disagree, investigate: heavy-tailed outcomes, small samples, or contamination usually explain it.

---

## 7. Power Analysis

### 7.1 Pre-test sample size (prospective)

For a two-proportion test, sample size per variant:

$$n = \frac{(z_{1-\alpha/2} \sqrt{2\bar{p}(1-\bar{p})} + z_{1-\beta} \sqrt{p_1(1-p_1) + p_2(1-p_2)})^2}{(p_2 - p_1)^2}$$

where $z_{1-\alpha/2}$ is the critical value for type I error and $z_{1-\beta}$ for power.

**Applied in:** The Experiment Designer tool, giving PMs a realistic view of required sample sizes before they commit.

### 7.2 Post-hoc power analysis (E5 diagnostic)

After seeing a non-significant result, we computed:

$$\text{Cohen's } d = \frac{|\hat{\mu}_T - \hat{\mu}_C|}{\sqrt{\frac{s_T^2 + s_C^2}{2}}}$$

Then, the actual power to detect that effect given the realized sample size. For E5:

- Cohen's d ≈ 0.04
- Observed sample: 2,907 per variant  
- Post-hoc power: **31%**

**How to read this:** We had a 31% chance of finding a significant result even if the effect we observed is real. Non-significance here is much more consistent with "underpowered test" than with "no effect."

### 7.3 The post-hoc power controversy

Some statisticians (notably Hoenig & Heisey, 2001) argue post-hoc power computed directly from the observed effect is deterministic with the p-value and adds nothing. That critique is valid if power is used to "retrospectively validate" a significant result.

The use here is different. We compute post-hoc power *given the observed effect* to answer the question: **"If the true effect is close to what we observed, was our test capable of detecting it?"** This is a diagnostic for test design adequacy, not a post-hoc claim about the underlying hypothesis.

The correct response to "power is 31%" isn't "therefore there's no effect." It's "our test couldn't have detected this effect reliably even if it exists; re-run with appropriate sample size."

---

## 8. Segment Analysis & Simpson's Paradox

**Applied to:** E2 (Extended Trial experiment).

### 8.1 The phenomenon

In E2, the overall treatment effect was:
- Overall: −4.04%, p = 0.086 (non-significant, appears flat)

But segment-level analysis revealed:
- New users (24% of mix): **+22.9%**, p < 0.01
- Returning users (35% of mix): −8.2%, p = 0.044
- Tenured users (40% of mix): −8.0%, p < 0.01

This is Simpson's paradox: the aggregate direction (negative) is opposite the direction in the majority segment (positive for new users), because the population mix weights heavily toward segments where treatment is negative.

### 8.2 Multiple comparisons

When testing K segments, we increase the chance of at least one false positive. For K = 3 segments, at α = 0.05, the family-wise error rate is up to 14%.

**What we did NOT do:** Apply Bonferroni correction to the segment analysis.

**Why:** Bonferroni corrects for multiple *hypotheses*. The segment analysis is not testing three independent hypotheses — it's decomposing a single business question ("does this work and for whom"). The correct response to multiple comparisons concerns is:

1. Pre-specify segments of interest before analysis
2. Require consistency with a business theory (why would new users differ from tenured?)
3. Validate with a holdout re-run if the stakes are high

For E2, the new-user result is not just statistically large but also business-intuitive (they have more time to evaluate the product, so longer trials help them more).

### 8.3 When to segment vs. when not to

**Segment when:**
- There's a prior business hypothesis about why segments should differ
- The segment is large enough for sufficient power
- The decision is actionable at the segment level (can we actually ship to only new users?)

**Don't segment when:**
- Searching for any segment that "wins" after seeing flat overall results (p-hacking)
- Segments are too small to distinguish signal from noise
- The business can't act on segment-level decisions anyway

---

## 9. Novelty Effect Detection

**Applied to:** E3 (Push Notification Time Shift).

### 9.1 Weekly decomposition

We segmented the 4-week test into weekly windows and computed the lift in each:

| Week | Observed lift |
|------|---------------|
| 1 | +14.6% |
| 2 | +9.0% |
| 3 | +3.0% |
| 4 | +2.4% |

### 9.2 Decay estimation

Fit $\log(\text{lift}_t) = a + b \cdot t$ to extract the half-life:

$$t_{1/2} = \frac{-\log(2)}{b}$$

For E3, $t_{1/2} \approx 1.1$ weeks. The effect decays rapidly.

### 9.3 Why this matters

A 1-week or 2-week test would have shown a "+14.6% win" and shipped. The true steady-state effect is ~2.4%, below any reasonable ship threshold when accounting for guardrail risks.

**Policy implication (from E3):** Any experiment whose mechanism is "users will notice something new" (notifications, UI, features) requires a minimum 3-week runtime. This is non-negotiable, because the cost of false positives here (shipping reverting behaviors) is much higher than the cost of waiting one more week.

---

## 10. Holdout Validation

**Applied to:** E6 (Leaderboard).

### 10.1 Design

- 45% control
- 45% treatment
- 10% holdout (remains unexposed to treatment even after ship)

### 10.2 The two validations holdout enables

**Pre-ship validation:** Control vs. holdout should show no meaningful difference. If they do, either:
- Control is contaminated (some treatment exposure leaked)
- Holdout was sampled from a systematically different population
- There's interaction with another live experiment

For E6: Control vs. holdout difference was +0.39% (p > 0.3) — passed.

**Post-ship validation:** After shipping, the holdout continues to receive control experience. If the treatment effect diminishes or reverses over time (because of novelty decay, seasonality interaction, or untested subpopulations), the holdout signals it.

### 10.3 When holdouts are worth the opportunity cost

- ✓ Major feature affecting >500K users
- ✓ High-confidence ship where post-ship monitoring is valuable
- ✓ Feature you might want to roll back if conditions change

Smaller tests don't justify holdouts. The 10% not getting the improvement costs real revenue.

---

## 11. Business Impact Modeling

**Applied to:** E2 (segment-level ship), E4 (kill decision), E6 (ship decision).

### 11.1 E4 — Net revenue impact calculation

$$\Delta \text{Revenue}_{\text{annual}} = N_{\text{annual new users}} \times [\Delta \text{Activation} \cdot \text{LTV}_{\text{non-retained}} + \Delta \text{D30 Retention} \cdot \text{LTV}_{\text{retained}}]$$

For E4, with stated assumptions:
- +$417K from marginal D1 activations (low-LTV, non-retaining users)
- −$1,115K from lost D30-retained users (high-LTV)
- Net: **−$697K/year**

### 11.2 Decision framework

The KILL decision on E4 isn't driven by statistical significance — it's driven by the business model. Even if E4's effects were borderline significant, the *direction* of impact (trading high-value retained users for low-value drop-offs) makes it a kill regardless.

**This is the analytics professional's real value-add:** not running the test, but translating the test into a decision-quality recommendation that respects the underlying economics.

### 11.3 Caveats on business impact numbers

All dollar figures depend on assumptions:

- Annual new-user volume
- LTV estimates (which have their own uncertainty)
- Conversion assumptions for projection windows

These numbers are **illustrative of the methodology**, not precise forecasts. In production, we'd:
- Use ranges instead of point estimates
- Feed posterior distributions from the Bayesian analysis into the business calc
- Document sensitivity to each key assumption

---

## References

Key sources informing this methodology:

- Deng, Xu, Kohavi, Walker (2013). *Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data* (CUPED)
- Kohavi, Tang, Xu (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing*
- Hoenig & Heisey (2001). *The Abuse of Power: The Pervasive Fallacy of Power Calculations for Data Analysis*
- Fabijan et al. (2019). *Sample Ratio Mismatch Checks in A/B Experiments at Microsoft*

---

*For the business narrative and decision reasoning behind these analyses, see the [main README](README.md) and the interactive dashboard.*
