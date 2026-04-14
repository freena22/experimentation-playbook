"""
=============================================================================
LinguaLeap Experimentation Program - Data Generation
=============================================================================
Generates simulated data for 6 experiments. Each experiment is designed
to embed a specific "teaching moment" while remaining statistically realistic.

Ground truth effects are deliberately set to teach specific lessons:
  E1: Clean winner, segments consistent         -> SHIP
  E2: Flat average hiding opposite segment effects -> SHIP TO SEGMENT
  E3: Novelty effect that decays                  -> KILL
  E4: Primary metric wins but north star loses    -> KILL
  E5: True positive effect, but underpowered      -> RE-RUN
  E6: Clean winner with holdout validation        -> SHIP
=============================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(2025)
os.makedirs('/home/claude/experiments', exist_ok=True)

# =============================================================================
# Helper: assign users to variants with randomization
# =============================================================================
def assign_variants(n_users, ratio=0.5, srm_violation=False):
    """Assign users to A/B. If srm_violation, introduce imbalance."""
    if srm_violation:
        # ~53/47 instead of 50/50 - enough to fail SRM check
        probs = [0.53, 0.47]
    else:
        probs = [1 - ratio, ratio]
    return np.random.choice(['control', 'treatment'], size=n_users, p=probs)


# =============================================================================
# E1 — Social Login at Signup (CLEAN WINNER)
# Teaching moment: Textbook example of what a clean ship looks like
# Ground truth: +9% signup completion, consistent across segments
# =============================================================================
print("=" * 70)
print("E1: Social Login at Signup")
print("=" * 70)

n = 45000
users = pd.DataFrame({
    'user_id': range(1, n+1),
    'variant': assign_variants(n),
    'country_tier': np.random.choice(['tier_1', 'tier_2', 'tier_3'], n, p=[0.4, 0.35, 0.25]),
    'device': np.random.choice(['ios', 'android'], n, p=[0.45, 0.55]),
    'traffic_source': np.random.choice(['organic', 'paid_social', 'paid_search', 'referral'], n, p=[0.35, 0.3, 0.2, 0.15]),
    'exposure_date': pd.date_range('2025-07-01', '2025-07-14', periods=n).date,
})

# Baseline signup completion: 62% in control
# Treatment lift: +9% (relative), so treatment = 67.6%
# Consistent across segments
base_rate = 0.62
lift = 0.09

users['completed_signup'] = 0
control_mask = users['variant'] == 'control'
treat_mask = users['variant'] == 'treatment'

users.loc[control_mask, 'completed_signup'] = np.random.binomial(1, base_rate, control_mask.sum())
users.loc[treat_mask, 'completed_signup'] = np.random.binomial(1, base_rate * (1 + lift), treat_mask.sum())

users.to_csv('/home/claude/experiments/E1_social_login.csv', index=False)
print(f"  Users: {n:,}")
print(f"  Control completion: {users[control_mask]['completed_signup'].mean():.3f}")
print(f"  Treatment completion: {users[treat_mask]['completed_signup'].mean():.3f}")
print(f"  Observed lift: {(users[treat_mask]['completed_signup'].mean() / users[control_mask]['completed_signup'].mean() - 1)*100:.2f}%")


# =============================================================================
# E2 — Extended Free Trial (HETEROGENEOUS EFFECTS)
# Teaching moment: Average effect ~0 hides opposing segment effects
# Ground truth: new users +18%, tenured users -8%
# =============================================================================
print("\n" + "=" * 70)
print("E2: Extended Trial 7d -> 14d")
print("=" * 70)

n = 38000
users = pd.DataFrame({
    'user_id': range(100001, 100001+n),
    'variant': assign_variants(n),
    # Adjusted mix: fewer new users, more tenured, to make overall effect flat
    'user_tenure': np.random.choice(['new', 'returning', 'tenured'], n, p=[0.25, 0.35, 0.40]),
    'country_tier': np.random.choice(['tier_1', 'tier_2', 'tier_3'], n, p=[0.35, 0.35, 0.3]),
    'exposure_date': pd.date_range('2025-07-15', '2025-08-05', periods=n).date,
})

# Baseline trial->paid conversion by tenure
base_rates = {'new': 0.08, 'returning': 0.14, 'tenured': 0.22}

# Treatment effect by tenure (KEY: opposing effects)
# Adjusted to make overall effect closer to flat
treatment_lift = {
    'new': 0.18,        # +18% new users love longer trial
    'returning': -0.02, # slightly negative
    'tenured': -0.10,   # -10% tenured users delay commitment
}

users['converted_to_paid'] = 0
for tenure in ['new', 'returning', 'tenured']:
    base = base_rates[tenure]
    lift = treatment_lift[tenure]
    
    control_ix = (users['variant'] == 'control') & (users['user_tenure'] == tenure)
    treat_ix = (users['variant'] == 'treatment') & (users['user_tenure'] == tenure)
    
    users.loc[control_ix, 'converted_to_paid'] = np.random.binomial(1, base, control_ix.sum())
    users.loc[treat_ix, 'converted_to_paid'] = np.random.binomial(1, base * (1 + lift), treat_ix.sum())

users.to_csv('/home/claude/experiments/E2_extended_trial.csv', index=False)
print(f"  Users: {n:,}")
print(f"  Overall control: {users[users['variant']=='control']['converted_to_paid'].mean():.4f}")
print(f"  Overall treatment: {users[users['variant']=='treatment']['converted_to_paid'].mean():.4f}")
overall_lift = (users[users['variant']=='treatment']['converted_to_paid'].mean() / users[users['variant']=='control']['converted_to_paid'].mean() - 1) * 100
print(f"  Overall lift: {overall_lift:.2f}% (should look ~flat)")
print(f"  By segment:")
for tenure in ['new', 'returning', 'tenured']:
    c = users[(users['variant']=='control') & (users['user_tenure']==tenure)]['converted_to_paid'].mean()
    t = users[(users['variant']=='treatment') & (users['user_tenure']==tenure)]['converted_to_paid'].mean()
    print(f"    {tenure:10s}: control={c:.4f}, treat={t:.4f}, lift={(t/c-1)*100:+.1f}%")


# =============================================================================
# E3 — Push Notification Time Shift (NOVELTY EFFECT)
# Teaching moment: Short-term win decays into noise
# Ground truth: Week 1: +15%, Week 2: +9%, Week 3: +4%, Week 4: +2%
# =============================================================================
print("\n" + "=" * 70)
print("E3: Push Time Shift (8am -> 8pm)")
print("=" * 70)

n_users = 52000
user_ids = np.arange(200001, 200001+n_users)
variants = assign_variants(n_users)

# Generate 4 weeks of daily push opens per user
records = []
base_open_rate = 0.18  # baseline daily push open rate

# Weekly lift pattern - novelty decay
weekly_lift = [0.15, 0.09, 0.04, 0.02]  # Week 1-4

for week_num in range(4):
    lift = weekly_lift[week_num]
    for day_in_week in range(7):
        day_idx = week_num * 7 + day_in_week
        date = pd.Timestamp('2025-07-15') + pd.Timedelta(days=day_idx)
        
        for uid, var in zip(user_ids, variants):
            if var == 'control':
                opened = np.random.binomial(1, base_open_rate)
            else:
                opened = np.random.binomial(1, base_open_rate * (1 + lift))
            records.append({'user_id': uid, 'variant': var, 'date': date.date(),
                          'week': week_num + 1, 'opened_push': opened})

df_e3 = pd.DataFrame(records)
df_e3.to_csv('/home/claude/experiments/E3_push_time.csv', index=False)
print(f"  User-days: {len(df_e3):,}")
print(f"  Weekly observed lift:")
for w in range(1, 5):
    wk = df_e3[df_e3['week']==w]
    c = wk[wk['variant']=='control']['opened_push'].mean()
    t = wk[wk['variant']=='treatment']['opened_push'].mean()
    print(f"    Week {w}: control={c:.4f}, treat={t:.4f}, lift={(t/c-1)*100:+.2f}%")


# =============================================================================
# E4 — Shortened Onboarding (SHORT-TERM WIN, LONG-TERM LOSS)
# Teaching moment: Primary metric vs North Star divergence
# Ground truth: +12% D1 activation BUT -4% D7 retention, -7% D30 retention
# =============================================================================
print("\n" + "=" * 70)
print("E4: Onboarding 5 steps -> 3 steps")
print("=" * 70)

n = 41000
users = pd.DataFrame({
    'user_id': range(300001, 300001+n),
    'variant': assign_variants(n),
    'country_tier': np.random.choice(['tier_1', 'tier_2', 'tier_3'], n, p=[0.4, 0.35, 0.25]),
    'exposure_date': pd.date_range('2025-07-01', '2025-07-14', periods=n).date,
})

# D1 activation (primary metric)
base_d1 = 0.45
d1_lift = 0.12
users['d1_activated'] = 0
for var, lift in [('control', 0), ('treatment', d1_lift)]:
    mask = users['variant'] == var
    users.loc[mask, 'd1_activated'] = np.random.binomial(1, base_d1 * (1 + lift), mask.sum())

# D7 retention (conditional on D1 activation)
# Key insight: treatment "activates" more users but those users are less committed
# because they skipped the onboarding that built habit
base_d7_given_d1 = 0.55  # of D1 activated users, 55% still active at D7 in control
d7_conditional_lift = -0.08  # among activated users, treatment actually retains fewer

users['d7_retained'] = 0
for var, cond_lift in [('control', 0), ('treatment', d7_conditional_lift)]:
    mask = (users['variant'] == var) & (users['d1_activated'] == 1)
    users.loc[mask, 'd7_retained'] = np.random.binomial(1, base_d7_given_d1 * (1 + cond_lift), mask.sum())

# D30 retention (deeper drop for treatment)
base_d30_given_d7 = 0.45
d30_conditional_lift = -0.06

users['d30_retained'] = 0
for var, cond_lift in [('control', 0), ('treatment', d30_conditional_lift)]:
    mask = (users['variant'] == var) & (users['d7_retained'] == 1)
    users.loc[mask, 'd30_retained'] = np.random.binomial(1, base_d30_given_d7 * (1 + cond_lift), mask.sum())

users.to_csv('/home/claude/experiments/E4_onboarding.csv', index=False)
print(f"  Users: {n:,}")
for metric in ['d1_activated', 'd7_retained', 'd30_retained']:
    c = users[users['variant']=='control'][metric].mean()
    t = users[users['variant']=='treatment'][metric].mean()
    lift = (t/c - 1) * 100
    print(f"  {metric:15s}: control={c:.4f}, treat={t:.4f}, lift={lift:+.2f}%")


# =============================================================================
# E5 — AI Conversation Practice (UNDERPOWERED)
# Teaching moment: Non-significance != no effect; MDE was too ambitious
# Ground truth: Real effect is +3% engagement, but MDE was designed for +8%
# =============================================================================
print("\n" + "=" * 70)
print("E5: AI Conversation Practice Feature")
print("=" * 70)

# Smaller sample size - what went wrong: team sized for MDE=8% but true effect is ~2%
# Result: truly underpowered test with p-value likely non-significant
n = 6000
users = pd.DataFrame({
    'user_id': range(400001, 400001+n),
    'variant': assign_variants(n),
    'device': np.random.choice(['ios', 'android'], n, p=[0.5, 0.5]),
    'exposure_date': pd.date_range('2025-08-01', '2025-08-14', periods=n).date,
})

# 14-day engagement (sessions count)
base_sessions = 8.5  # baseline avg sessions in 14 days
true_lift = 0.02  # +2% real effect (small but real)

users['sessions_14d'] = 0
for var, lift in [('control', 0), ('treatment', true_lift)]:
    mask = users['variant'] == var
    mean_val = base_sessions * (1 + lift)
    # Poisson-ish distribution with overdispersion
    users.loc[mask, 'sessions_14d'] = np.random.negative_binomial(
        n=3, p=3/(3+mean_val), size=mask.sum()
    )

users.to_csv('/home/claude/experiments/E5_ai_practice.csv', index=False)
print(f"  Users: {n:,} (underpowered)")
c_mean = users[users['variant']=='control']['sessions_14d'].mean()
t_mean = users[users['variant']=='treatment']['sessions_14d'].mean()
print(f"  Control mean sessions: {c_mean:.3f}")
print(f"  Treatment mean sessions: {t_mean:.3f}")
print(f"  Observed lift: {(t_mean/c_mean - 1)*100:+.2f}%")
from scipy import stats
c_data = users[users['variant']=='control']['sessions_14d']
t_data = users[users['variant']=='treatment']['sessions_14d']
t_stat, p_val = stats.ttest_ind(t_data, c_data)
print(f"  p-value: {p_val:.4f} (likely not significant at 0.05)")


# =============================================================================
# E6 — Leaderboard Gamification (CLEAN WIN WITH HOLDOUT)
# Teaching moment: Properly designed and validated experiment
# Ground truth: +22% DAU, strong effect, confirmed with 10% holdout
# =============================================================================
print("\n" + "=" * 70)
print("E6: Leaderboard Gamification")
print("=" * 70)

n = 58000
# 45% control, 45% treatment, 10% holdout (no treatment, continued measurement)
variant_assignment = np.random.choice(
    ['control', 'treatment', 'holdout'], n, p=[0.45, 0.45, 0.10]
)

users = pd.DataFrame({
    'user_id': range(500001, 500001+n),
    'variant': variant_assignment,
    'country_tier': np.random.choice(['tier_1', 'tier_2', 'tier_3'], n, p=[0.4, 0.35, 0.25]),
    'pre_period_sessions': np.random.negative_binomial(5, 5/15, n),  # for CUPED
    'exposure_date': pd.date_range('2025-08-10', '2025-09-10', periods=n).date,
})

# 30-day avg DAU (days active out of 30)
base_dau_days = 12.0
lift_treatment = 0.22

users['active_days_30'] = 0
# Control & Holdout: same underlying behavior (to validate)
# CUPED pre-period correlation built in
for var in ['control', 'treatment', 'holdout']:
    mask = users['variant'] == var
    # Add correlation with pre-period
    pre = users.loc[mask, 'pre_period_sessions'].values
    # Normalize pre-period (centered)
    pre_centered = (pre - pre.mean()) / (pre.std() + 1e-9)
    
    if var == 'treatment':
        effective_mean = base_dau_days * (1 + lift_treatment)
    else:
        effective_mean = base_dau_days
    
    # Base draw + CUPED-friendly correlation + cap at 30
    draws = np.random.normal(effective_mean, 4.5, mask.sum())
    draws += pre_centered * 2.5  # correlation with pre-period
    draws = np.clip(draws, 0, 30).round().astype(int)
    users.loc[mask, 'active_days_30'] = draws

users.to_csv('/home/claude/experiments/E6_leaderboard.csv', index=False)
print(f"  Users: {n:,}")
print(f"  Variant split:")
for v in ['control', 'treatment', 'holdout']:
    d = users[users['variant']==v]
    print(f"    {v:10s}: n={len(d):,}, avg active days={d['active_days_30'].mean():.2f}")
t_mean = users[users['variant']=='treatment']['active_days_30'].mean()
c_mean = users[users['variant']=='control']['active_days_30'].mean()
h_mean = users[users['variant']=='holdout']['active_days_30'].mean()
print(f"  Treatment vs Control lift: {(t_mean/c_mean-1)*100:+.2f}%")
print(f"  Control vs Holdout (should be ~0): {(c_mean/h_mean-1)*100:+.2f}%")


# =============================================================================
# Cookie Cats Reproduction — based on public distribution specs
# =============================================================================
print("\n" + "=" * 70)
print("Cookie Cats (reproduced from public dataset specs)")
print("=" * 70)

# Based on the actual Cookie Cats dataset characteristics:
# - 90,189 users
# - ~50/50 split between gate_30 and gate_40
# - 1-day retention: gate_30 ~44.8%, gate_40 ~44.2% (gate_30 slightly higher)
# - 7-day retention: gate_30 ~19.0%, gate_40 ~18.2% (gate_30 meaningfully higher)
# - sum_gamerounds: heavily right-skewed, log-normal-ish

n_cc = 90189
np.random.seed(42)

variant_cc = np.random.choice(['gate_30', 'gate_40'], n_cc, p=[0.5024, 0.4976])  # actual split
userid = np.arange(116, 116 + n_cc)

# Game rounds - heavily right-skewed, some with massive values
# Using mixture: most users play little, some play a lot
is_heavy = np.random.random(n_cc) < 0.12
gamerounds = np.where(
    is_heavy,
    np.random.negative_binomial(2, 0.01, n_cc),  # heavy players
    np.random.negative_binomial(2, 0.08, n_cc)   # light players
)
gamerounds = np.clip(gamerounds, 0, 50000)

# 1-day retention: slightly lower in gate_40 (but not significantly)
p_ret1_gate30 = 0.4482
p_ret1_gate40 = 0.4423

# 7-day retention: meaningfully lower in gate_40
p_ret7_gate30 = 0.1902
p_ret7_gate40 = 0.1820

ret_1 = np.zeros(n_cc, dtype=bool)
ret_7 = np.zeros(n_cc, dtype=bool)

mask_30 = variant_cc == 'gate_30'
mask_40 = variant_cc == 'gate_40'

# Retention correlated with gamerounds (real-world effect: more play → more retention)
# Adjusted offsets so that marginal retention matches Cookie Cats' published values
# gate_30: ret_1 ≈ 44.8%, ret_7 ≈ 19.0%
# gate_40: ret_1 ≈ 44.2%, ret_7 ≈ 18.2%
round_effect = np.tanh(gamerounds / 50)  # 0 to 1 sigmoid-like

ret_1[mask_30] = np.random.random(mask_30.sum()) < (p_ret1_gate30 + 0.15 * round_effect[mask_30] - 0.06)
ret_1[mask_40] = np.random.random(mask_40.sum()) < (p_ret1_gate40 + 0.15 * round_effect[mask_40] - 0.06)

# For ret_7, we need higher base rates because of the "ret_7 requires ret_1" constraint
# If we want final ret_7 ≈ 19%, and ret_7 only happens for ret_1 users (~45%),
# then among ret_1 users we need ~42% to also be ret_7
ret_7_raw_30 = np.random.random(mask_30.sum()) < (0.42 + 0.15 * round_effect[mask_30])
ret_7_raw_40 = np.random.random(mask_40.sum()) < (0.405 + 0.15 * round_effect[mask_40])

ret_7[mask_30] = ret_7_raw_30
ret_7[mask_40] = ret_7_raw_40

# 7-day retention requires 1-day retention (logical constraint)
ret_7 = ret_7 & ret_1

cookie_cats = pd.DataFrame({
    'userid': userid,
    'version': variant_cc,
    'sum_gamerounds': gamerounds,
    'retention_1': ret_1,
    'retention_7': ret_7,
})
cookie_cats.to_csv('/home/claude/experiments/cookie_cats.csv', index=False)
print(f"  Users: {len(cookie_cats):,}")
print(f"  Split:")
print(f"    gate_30: {(cookie_cats['version']=='gate_30').sum():,}")
print(f"    gate_40: {(cookie_cats['version']=='gate_40').sum():,}")
print(f"  1-day retention:")
print(f"    gate_30: {cookie_cats[cookie_cats['version']=='gate_30']['retention_1'].mean():.4f}")
print(f"    gate_40: {cookie_cats[cookie_cats['version']=='gate_40']['retention_1'].mean():.4f}")
print(f"  7-day retention:")
print(f"    gate_30: {cookie_cats[cookie_cats['version']=='gate_30']['retention_7'].mean():.4f}")
print(f"    gate_40: {cookie_cats[cookie_cats['version']=='gate_40']['retention_7'].mean():.4f}")
print(f"  Gamerounds: median={cookie_cats['sum_gamerounds'].median():.0f}, "
      f"mean={cookie_cats['sum_gamerounds'].mean():.1f}, max={cookie_cats['sum_gamerounds'].max():,}")


print("\n" + "=" * 70)
print("DATA GENERATION COMPLETE")
print("=" * 70)
for f in sorted(os.listdir('/home/claude/experiments')):
    size = os.path.getsize(f'/home/claude/experiments/{f}') / 1024
    print(f"  {f:30s} {size:7.1f} KB")
