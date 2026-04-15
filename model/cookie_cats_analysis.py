"""
=============================================================================
COOKIE CATS DEEP DIVE
=============================================================================
The classic mobile A/B test: gate placement at level 30 vs level 40.
This analysis shows what hands-on work on real (or realistic) data looks like.

Key analytical steps:
  1. Data quality & sanity checks
  2. SRM (Sample Ratio Mismatch) check  
  3. Outlier diagnosis (sum_gamerounds heavy tail)
  4. Primary metric analysis: 1-day & 7-day retention
  5. Bayesian inference with proper uncertainty quantification
  6. Bootstrap CI for non-parametric robustness
  7. Engagement segmentation (light vs heavy players)
  8. Statistical decision + business interpretation
=============================================================================
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import beta as beta_dist
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = _ROOT / "data" / "experiments"
RESULTS_DIR = _ROOT / "data" / "results"
CHARTS_DIR = _ROOT / "charts"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
np.random.seed(2025)

COLORS = {
    'gate_30': '#3B82F6',
    'gate_40': '#EF4444',
    'neutral': '#6B7280',
    'positive': '#10B981',
    'warning': '#F59E0B',
}

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#9CA3AF',
    'axes.linewidth': 0.8,
    'axes.titleweight': 'bold',
    'axes.titlesize': 12,
})


print("=" * 70)
print("COOKIE CATS DEEP DIVE")
print("=" * 70)

df = pd.read_csv(EXPERIMENTS_DIR / 'cookie_cats.csv')
print(f"\nDataset: {len(df):,} users")
print(f"Variants: {df['version'].value_counts().to_dict()}")
print(f"\nFirst rows:")
print(df.head())

# ============================================================================
# STEP 1: Data Quality Checks
# ============================================================================
print("\n" + "=" * 70)
print("STEP 1: DATA QUALITY")
print("=" * 70)

# Check for nulls
print(f"\nMissing values: {df.isna().sum().sum()}")

# Check distributions
print(f"\nsum_gamerounds distribution:")
print(f"  Min: {df['sum_gamerounds'].min()}")
print(f"  25%: {df['sum_gamerounds'].quantile(0.25)}")
print(f"  Median: {df['sum_gamerounds'].median()}")
print(f"  75%: {df['sum_gamerounds'].quantile(0.75)}")
print(f"  95%: {df['sum_gamerounds'].quantile(0.95)}")
print(f"  99%: {df['sum_gamerounds'].quantile(0.99)}")
print(f"  Max: {df['sum_gamerounds'].max()}")
print(f"  Skewness: {stats.skew(df['sum_gamerounds']):.2f} (heavily right-skewed)")

# Outlier identification (extreme players)
n_extreme = (df['sum_gamerounds'] > 1000).sum()
extreme_users_pct = n_extreme / len(df) * 100
print(f"\nExtreme users (>1000 rounds): {n_extreme} ({extreme_users_pct:.2f}%)")

# Logical consistency: ret_7 implies ret_1
inconsistent = ((df['retention_7'] == True) & (df['retention_1'] == False)).sum()
print(f"Logical consistency (ret_7 implies ret_1): {inconsistent} violations")

# ============================================================================
# STEP 2: SRM Check
# ============================================================================
print("\n" + "=" * 70)
print("STEP 2: SAMPLE RATIO MISMATCH CHECK")
print("=" * 70)

n_30 = (df['version'] == 'gate_30').sum()
n_40 = (df['version'] == 'gate_40').sum()
total = n_30 + n_40
expected_30 = total / 2
expected_40 = total / 2

chi2 = ((n_30 - expected_30)**2 / expected_30) + ((n_40 - expected_40)**2 / expected_40)
p_srm = 1 - stats.chi2.cdf(chi2, df=1)

print(f"\n  gate_30: {n_30:,} ({n_30/total*100:.2f}%)")
print(f"  gate_40: {n_40:,} ({n_40/total*100:.2f}%)")
print(f"  Chi-square: {chi2:.4f}, p-value: {p_srm:.4f}")
print(f"  SRM check: {'PASSED' if p_srm > 0.001 else 'FAILED'}")

# ============================================================================
# STEP 3: Primary metric — 1-day retention
# ============================================================================
print("\n" + "=" * 70)
print("STEP 3: 1-DAY RETENTION ANALYSIS")
print("=" * 70)

# By group
group_30 = df[df['version'] == 'gate_30']
group_40 = df[df['version'] == 'gate_40']

ret1_30 = group_30['retention_1'].mean()
ret1_40 = group_40['retention_1'].mean()
ret1_diff = ret1_40 - ret1_30
ret1_lift = (ret1_40 / ret1_30 - 1) * 100

# Two-proportion z-test
n1, x1 = len(group_30), group_30['retention_1'].sum()
n2, x2 = len(group_40), group_40['retention_1'].sum()
p_pool = (x1 + x2) / (n1 + n2)
se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
z_stat = (x2/n2 - x1/n1) / se
p_value_1d = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# CI on difference
se_diff = np.sqrt(ret1_30*(1-ret1_30)/n1 + ret1_40*(1-ret1_40)/n2)
ci_lower = ret1_diff - 1.96 * se_diff
ci_upper = ret1_diff + 1.96 * se_diff

print(f"\n  gate_30 1-day retention: {ret1_30:.4f} ({ret1_30*100:.2f}%)")
print(f"  gate_40 1-day retention: {ret1_40:.4f} ({ret1_40*100:.2f}%)")
print(f"  Absolute difference: {ret1_diff*100:+.3f}pp")
print(f"  Relative lift:       {ret1_lift:+.2f}%")
print(f"  95% CI on diff:      [{ci_lower*100:+.3f}pp, {ci_upper*100:+.3f}pp]")
print(f"  z-stat: {z_stat:.3f}, p-value: {p_value_1d:.4f}")
print(f"  Significant at α=0.05: {'YES' if p_value_1d < 0.05 else 'NO'}")

# ============================================================================
# STEP 4: 7-day retention (the more important metric)
# ============================================================================
print("\n" + "=" * 70)
print("STEP 4: 7-DAY RETENTION ANALYSIS")
print("=" * 70)

ret7_30 = group_30['retention_7'].mean()
ret7_40 = group_40['retention_7'].mean()
ret7_diff = ret7_40 - ret7_30
ret7_lift = (ret7_40 / ret7_30 - 1) * 100

x1_7, x2_7 = group_30['retention_7'].sum(), group_40['retention_7'].sum()
p_pool_7 = (x1_7 + x2_7) / (n1 + n2)
se_7 = np.sqrt(p_pool_7 * (1 - p_pool_7) * (1/n1 + 1/n2))
z_stat_7 = (x2_7/n2 - x1_7/n1) / se_7
p_value_7d = 2 * (1 - stats.norm.cdf(abs(z_stat_7)))

se_diff_7 = np.sqrt(ret7_30*(1-ret7_30)/n1 + ret7_40*(1-ret7_40)/n2)
ci_lower_7 = ret7_diff - 1.96 * se_diff_7
ci_upper_7 = ret7_diff + 1.96 * se_diff_7

print(f"\n  gate_30 7-day retention: {ret7_30:.4f} ({ret7_30*100:.2f}%)")
print(f"  gate_40 7-day retention: {ret7_40:.4f} ({ret7_40*100:.2f}%)")
print(f"  Absolute difference: {ret7_diff*100:+.3f}pp")
print(f"  Relative lift:       {ret7_lift:+.2f}%")
print(f"  95% CI on diff:      [{ci_lower_7*100:+.3f}pp, {ci_upper_7*100:+.3f}pp]")
print(f"  z-stat: {z_stat_7:.3f}, p-value: {p_value_7d:.4f}")
print(f"  Significant at α=0.05: {'YES' if p_value_7d < 0.05 else 'NO'}")

# ============================================================================
# STEP 5: Bayesian Analysis (Beta-Binomial)
# ============================================================================
print("\n" + "=" * 70)
print("STEP 5: BAYESIAN INFERENCE")
print("=" * 70)

# Uniform prior Beta(1,1)
n_sim = 100000

# 1-day
post_30_d1 = beta_dist(1 + x1, 1 + n1 - x1).rvs(n_sim)
post_40_d1 = beta_dist(1 + x2, 1 + n2 - x2).rvs(n_sim)

p_gate30_better_d1 = (post_30_d1 > post_40_d1).mean()
expected_lift_d1 = (post_40_d1 - post_30_d1).mean()

# 7-day
post_30_d7 = beta_dist(1 + x1_7, 1 + n1 - x1_7).rvs(n_sim)
post_40_d7 = beta_dist(1 + x2_7, 1 + n2 - x2_7).rvs(n_sim)

p_gate30_better_d7 = (post_30_d7 > post_40_d7).mean()
expected_lift_d7 = (post_40_d7 - post_30_d7).mean()

# Probability that gate_40 hurts retention by at least 1 percentage point
prob_d7_loss_1pp = ((post_30_d7 - post_40_d7) > 0.01).mean()

print(f"\n  1-day retention:")
print(f"    P(gate_30 > gate_40): {p_gate30_better_d1:.4f}")
print(f"    Expected diff (gate_40 - gate_30): {expected_lift_d1*100:+.3f}pp")
print(f"\n  7-day retention:")
print(f"    P(gate_30 > gate_40): {p_gate30_better_d7:.4f}")
print(f"    Expected diff (gate_40 - gate_30): {expected_lift_d7*100:+.3f}pp")
print(f"    P(gate_40 hurts retention by ≥1pp): {prob_d7_loss_1pp:.4f}")

# ============================================================================
# STEP 6: Bootstrap CI for robustness
# ============================================================================
print("\n" + "=" * 70)
print("STEP 6: BOOTSTRAP VALIDATION")
print("=" * 70)

n_boot = 5000
ret7_diffs_boot = []
ret1_diffs_boot = []

for _ in range(n_boot):
    boot_idx_30 = np.random.choice(n1, n1, replace=True)
    boot_idx_40 = np.random.choice(n2, n2, replace=True)
    
    sample_30_ret1 = group_30['retention_1'].values[boot_idx_30].mean()
    sample_40_ret1 = group_40['retention_1'].values[boot_idx_40].mean()
    sample_30_ret7 = group_30['retention_7'].values[boot_idx_30].mean()
    sample_40_ret7 = group_40['retention_7'].values[boot_idx_40].mean()
    
    ret1_diffs_boot.append(sample_40_ret1 - sample_30_ret1)
    ret7_diffs_boot.append(sample_40_ret7 - sample_30_ret7)

ret1_diffs_boot = np.array(ret1_diffs_boot)
ret7_diffs_boot = np.array(ret7_diffs_boot)

print(f"\n  Bootstrap CI (5000 iterations):")
print(f"  1-day retention diff: 95% CI = [{np.percentile(ret1_diffs_boot, 2.5)*100:+.3f}pp, "
      f"{np.percentile(ret1_diffs_boot, 97.5)*100:+.3f}pp]")
print(f"  7-day retention diff: 95% CI = [{np.percentile(ret7_diffs_boot, 2.5)*100:+.3f}pp, "
      f"{np.percentile(ret7_diffs_boot, 97.5)*100:+.3f}pp]")

# ============================================================================
# STEP 7: Engagement segmentation
# ============================================================================
print("\n" + "=" * 70)
print("STEP 7: ENGAGEMENT-LEVEL SEGMENTATION")
print("=" * 70)

# Define engagement tiers
df['engagement_tier'] = pd.cut(
    df['sum_gamerounds'], 
    bins=[-1, 0, 5, 30, 100, np.inf],
    labels=['No play', 'Tried (1-5)', 'Light (6-30)', 'Engaged (31-100)', 'Heavy (100+)']
)

print(f"\n  User distribution by engagement:")
print(df['engagement_tier'].value_counts().sort_index())

print(f"\n  Retention by engagement tier:")
seg_results = {}
for tier in df['engagement_tier'].cat.categories:
    sub = df[df['engagement_tier'] == tier]
    if len(sub) < 100:
        continue
    sub_30 = sub[sub['version'] == 'gate_30']
    sub_40 = sub[sub['version'] == 'gate_40']
    if len(sub_30) < 50 or len(sub_40) < 50:
        continue
    
    r7_30 = sub_30['retention_7'].mean()
    r7_40 = sub_40['retention_7'].mean()
    diff = (r7_40 - r7_30) * 100
    
    seg_results[str(tier)] = {
        'n_total': len(sub),
        'n_gate_30': len(sub_30),
        'n_gate_40': len(sub_40),
        'ret7_gate_30': round(float(r7_30), 4),
        'ret7_gate_40': round(float(r7_40), 4),
        'abs_diff_pp': round(float(diff), 3),
    }
    print(f"    {tier:18s} (n={len(sub):5d}): "
          f"gate_30={r7_30*100:5.2f}%, gate_40={r7_40*100:5.2f}%, "
          f"diff={diff:+.2f}pp")

# ============================================================================
# STEP 8: Save results & visualization
# ============================================================================
print("\n" + "=" * 70)
print("STEP 8: BUSINESS DECISION & REPORT")
print("=" * 70)

cookie_results = {
    'experiment_name': 'Cookie Cats: Gate placement (level 30 vs level 40)',
    'data_source': 'Real public dataset (Kaggle, CC0 license)',
    'background': (
        'Cookie Cats is a popular mobile puzzle game. As players progress, '
        'they encounter "gates" that force them to either wait or pay to continue. '
        'The original gate was at level 30. This experiment moved it to level 40, '
        'on the hypothesis that delaying the gate would improve retention.'
    ),
    'sample_sizes': {
        'gate_30': int(n_30),
        'gate_40': int(n_40),
        'total': int(total),
        'split_pct': [round(n_30/total, 4), round(n_40/total, 4)]
    },
    'data_quality': {
        'missing_values': int(df.isna().sum().sum()),
        'logical_violations': int(inconsistent),
        'extreme_users_pct': round(extreme_users_pct, 3),
        'gamerounds_skewness': round(float(stats.skew(df['sum_gamerounds'])), 2),
    },
    'srm_check': {
        'chi2': round(float(chi2), 4),
        'p_value': round(float(p_srm), 4),
        'passed': bool(p_srm > 0.001),
    },
    'retention_1_day': {
        'gate_30_rate': round(float(ret1_30), 4),
        'gate_40_rate': round(float(ret1_40), 4),
        'absolute_diff_pp': round(float(ret1_diff*100), 3),
        'relative_lift_pct': round(float(ret1_lift), 2),
        'p_value': round(float(p_value_1d), 4),
        'ci_95_pp': [round(float(ci_lower*100), 3), round(float(ci_upper*100), 3)],
        'significant_at_05': bool(p_value_1d < 0.05),
    },
    'retention_7_day': {
        'gate_30_rate': round(float(ret7_30), 4),
        'gate_40_rate': round(float(ret7_40), 4),
        'absolute_diff_pp': round(float(ret7_diff*100), 3),
        'relative_lift_pct': round(float(ret7_lift), 2),
        'p_value': round(float(p_value_7d), 4),
        'ci_95_pp': [round(float(ci_lower_7*100), 3), round(float(ci_upper_7*100), 3)],
        'significant_at_05': bool(p_value_7d < 0.05),
    },
    'bayesian': {
        'd1_prob_gate30_better': round(float(p_gate30_better_d1), 4),
        'd7_prob_gate30_better': round(float(p_gate30_better_d7), 4),
        'd7_prob_gate40_loses_at_least_1pp': round(float(prob_d7_loss_1pp), 4),
    },
    'bootstrap': {
        'd1_diff_ci_95_pp': [round(float(np.percentile(ret1_diffs_boot, 2.5)*100), 3),
                             round(float(np.percentile(ret1_diffs_boot, 97.5)*100), 3)],
        'd7_diff_ci_95_pp': [round(float(np.percentile(ret7_diffs_boot, 2.5)*100), 3),
                             round(float(np.percentile(ret7_diffs_boot, 97.5)*100), 3)],
    },
    'engagement_segmentation': seg_results,
    'decision': 'KEEP GATE AT LEVEL 30 (do not move to level 40)',
    'business_interpretation': (
        'Both 1-day and 7-day retention are higher when the gate is at level 30. '
        'The 7-day retention difference is small in absolute terms (~0.8pp) but '
        'meaningful in relative terms and statistically significant. '
        'Bayesian analysis shows >99% probability that gate_30 retains better at day 7. '
        'Moving the gate later would reduce long-term player engagement.'
    ),
    'why_this_matters': (
        "This is a textbook example of why 'less friction = better' is too simple a heuristic. "
        "The forced wait at level 30 likely creates a habit-forming pause that players return from. "
        "Moving it to level 40 means more players hit the gate after they've already lost interest, "
        "rather than during peak engagement when they're motivated to come back."
    ),
}

with open(RESULTS_DIR / 'cookie_cats_results.json', 'w') as f:
    json.dump(cookie_results, f, indent=2)

print(f"\n  ★ DECISION: Keep gate at level 30")
print(f"  ★ 7-day retention is {ret7_lift:.2f}% higher with gate_30, p={p_value_7d:.3f}")
print(f"  ★ Bayesian P(gate_30 wins at D7) = {p_gate30_better_d7:.4f}")
print(f"\nResults saved to data/results/cookie_cats_results.json")
