"""
Cookie Cats deep-dive visualizations.
"""

import numpy as np
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import beta as beta_dist
from scipy import stats

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

df = pd.read_csv('/home/claude/experiments/cookie_cats.csv')
with open('/home/claude/results/cookie_cats_results.json') as f:
    results = json.load(f)

np.random.seed(42)


# ============================================================================
# CHART 1: Data quality / distribution overview
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Game rounds distribution (heavy tail)
ax = axes[0]
# Cap at 99th percentile for visual clarity
cap = df['sum_gamerounds'].quantile(0.99)
data_capped = df[df['sum_gamerounds'] <= cap]['sum_gamerounds']

ax.hist(data_capped, bins=50, color=COLORS['neutral'], alpha=0.7, edgecolor='white')
ax.axvline(df['sum_gamerounds'].median(), color=COLORS['positive'], 
          linestyle='--', linewidth=2, label=f'Median: {int(df["sum_gamerounds"].median())}')
ax.axvline(df['sum_gamerounds'].mean(), color=COLORS['warning'], 
          linestyle='--', linewidth=2, label=f'Mean: {df["sum_gamerounds"].mean():.1f}')

ax.set_xlabel('Sum of Game Rounds (capped at 99th percentile = 408)')
ax.set_ylabel('Number of Users')
ax.set_title(f'Game rounds: heavily right-skewed (skew={stats.skew(df["sum_gamerounds"]):.2f})', loc='left')
ax.legend()

ax.text(0.98, 0.85, f'Max: {df["sum_gamerounds"].max():,} rounds\n(top players play 50x median)',
       transform=ax.transAxes, ha='right', va='top', fontsize=9, color='#6B7280',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#F59E0B'))

# Right: SRM check
ax = axes[1]
srm = results['srm_check']
sample = results['sample_sizes']

variants = ['gate_30\n(control)', 'gate_40\n(treatment)']
counts = [sample['gate_30'], sample['gate_40']]
colors_v = [COLORS['gate_30'], COLORS['gate_40']]

bars = ax.bar(variants, counts, color=colors_v, alpha=0.75, edgecolor='white', linewidth=2, width=0.5)
for bar, c in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
           f'{c:,}\n({c/sum(counts)*100:.2f}%)', ha='center', fontweight='bold', fontsize=11)

ax.set_ylabel('Number of Users')
ax.set_ylim(0, max(counts) * 1.18)
ax.set_title(f'Sample Ratio Mismatch check: PASSED (p={srm["p_value"]:.3f})', loc='left')
ax.text(0.5, -0.18, f'χ² = {srm["chi2"]:.3f}  |  Expected 50/50, observed 50.17/49.83',
       transform=ax.transAxes, ha='center', fontsize=10, color='#6B7280', style='italic')

plt.suptitle('Cookie Cats: Data Quality & Sanity Checks', fontsize=14, fontweight='bold', y=1.02)
plt.savefig('/home/claude/charts/CC_01_data_quality.png', dpi=140, bbox_inches='tight',
           facecolor='white')
plt.close()
print("✓ CC_01_data_quality.png")


# ============================================================================
# CHART 2: Retention comparison (the core result)
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: 1-day retention
ax = axes[0]
r1 = results['retention_1_day']
rates_d1 = [r1['gate_30_rate']*100, r1['gate_40_rate']*100]
bars = ax.bar(['gate_30', 'gate_40'], rates_d1, color=[COLORS['gate_30'], COLORS['gate_40']],
             alpha=0.8, edgecolor='white', linewidth=2, width=0.5)
for bar, r in zip(bars, rates_d1):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
           f'{r:.2f}%', ha='center', fontweight='bold', fontsize=12)

ax.set_ylabel('1-Day Retention (%)')
ax.set_ylim(0, max(rates_d1) * 1.18)
ax.set_title(f'1-Day Retention: difference NOT significant (p={r1["p_value"]:.3f})', loc='left')

# Annotation
diff_d1 = r1['absolute_diff_pp']
ax.text(0.5, 0.92, f'Δ = {diff_d1:+.2f}pp\n95% CI: [{r1["ci_95_pp"][0]:+.2f}pp, {r1["ci_95_pp"][1]:+.2f}pp]',
       transform=ax.transAxes, ha='center', va='top', fontsize=10,
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#F3F4F6', edgecolor='#9CA3AF'))

# Right: 7-day retention
ax = axes[1]
r7 = results['retention_7_day']
rates_d7 = [r7['gate_30_rate']*100, r7['gate_40_rate']*100]
bars = ax.bar(['gate_30', 'gate_40'], rates_d7, color=[COLORS['gate_30'], COLORS['gate_40']],
             alpha=0.8, edgecolor='white', linewidth=2, width=0.5)
for bar, r in zip(bars, rates_d7):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
           f'{r:.2f}%', ha='center', fontweight='bold', fontsize=12)

ax.set_ylabel('7-Day Retention (%)')
ax.set_ylim(0, max(rates_d7) * 1.25)
ax.set_title(f'7-Day Retention: significantly LOWER for gate_40 (p={r7["p_value"]:.3f})', loc='left')

diff_d7 = r7['absolute_diff_pp']
ax.text(0.5, 0.92, f'Δ = {diff_d7:+.2f}pp\n95% CI: [{r7["ci_95_pp"][0]:+.2f}pp, {r7["ci_95_pp"][1]:+.2f}pp]',
       transform=ax.transAxes, ha='center', va='top', fontsize=10, fontweight='bold',
       color='#991B1B',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEE2E2', edgecolor='#EF4444'))

plt.suptitle('Cookie Cats: Retention Comparison\n7-day matters more than 1-day for engagement decisions',
            fontsize=14, fontweight='bold', y=1.05)
plt.savefig('/home/claude/charts/CC_02_retention.png', dpi=140, bbox_inches='tight',
           facecolor='white')
plt.close()
print("✓ CC_02_retention.png")


# ============================================================================
# CHART 3: Bayesian posterior distributions
# ============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

n1 = results['sample_sizes']['gate_30']
n2 = results['sample_sizes']['gate_40']

# 1-day posteriors
x1_d1 = int(n1 * results['retention_1_day']['gate_30_rate'])
x2_d1 = int(n2 * results['retention_1_day']['gate_40_rate'])

ax = axes[0]
post_30_d1 = beta_dist(1 + x1_d1, 1 + n1 - x1_d1)
post_40_d1 = beta_dist(1 + x2_d1, 1 + n2 - x2_d1)

x_range = np.linspace(0.44, 0.475, 1000)
ax.plot(x_range*100, post_30_d1.pdf(x_range), color=COLORS['gate_30'], linewidth=2.5, label='gate_30')
ax.fill_between(x_range*100, post_30_d1.pdf(x_range), alpha=0.2, color=COLORS['gate_30'])
ax.plot(x_range*100, post_40_d1.pdf(x_range), color=COLORS['gate_40'], linewidth=2.5, label='gate_40')
ax.fill_between(x_range*100, post_40_d1.pdf(x_range), alpha=0.2, color=COLORS['gate_40'])

ax.set_xlabel('1-Day Retention Rate (%)')
ax.set_ylabel('Posterior Density')
ax.set_title(f'1-day retention: posteriors overlap substantially', loc='left')
ax.legend(loc='upper right')
ax.text(0.02, 0.95, f'P(gate_30 > gate_40) = {results["bayesian"]["d1_prob_gate30_better"]:.3f}',
       transform=ax.transAxes, fontsize=10, va='top',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#F3F4F6', edgecolor='#9CA3AF'))

# 7-day posteriors
x1_d7 = int(n1 * results['retention_7_day']['gate_30_rate'])
x2_d7 = int(n2 * results['retention_7_day']['gate_40_rate'])

ax = axes[1]
post_30_d7 = beta_dist(1 + x1_d7, 1 + n1 - x1_d7)
post_40_d7 = beta_dist(1 + x2_d7, 1 + n2 - x2_d7)

x_range = np.linspace(0.21, 0.235, 1000)
ax.plot(x_range*100, post_30_d7.pdf(x_range), color=COLORS['gate_30'], linewidth=2.5, label='gate_30')
ax.fill_between(x_range*100, post_30_d7.pdf(x_range), alpha=0.2, color=COLORS['gate_30'])
ax.plot(x_range*100, post_40_d7.pdf(x_range), color=COLORS['gate_40'], linewidth=2.5, label='gate_40')
ax.fill_between(x_range*100, post_40_d7.pdf(x_range), alpha=0.2, color=COLORS['gate_40'])

ax.set_xlabel('7-Day Retention Rate (%)')
ax.set_ylabel('Posterior Density')
ax.set_title('7-day retention: posteriors clearly separated', loc='left')
ax.legend(loc='upper right')
ax.text(0.02, 0.95, 
       f'P(gate_30 > gate_40) = {results["bayesian"]["d7_prob_gate30_better"]:.4f}',
       transform=ax.transAxes, fontsize=10, va='top', fontweight='bold', color='#991B1B',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEE2E2', edgecolor='#EF4444'))

plt.suptitle('Cookie Cats: Bayesian Posterior Analysis\nUncertainty visualized — D1 ambiguous, D7 conclusive',
            fontsize=14, fontweight='bold', y=1.05)
plt.savefig('/home/claude/charts/CC_03_bayesian.png', dpi=140, bbox_inches='tight',
           facecolor='white')
plt.close()
print("✓ CC_03_bayesian.png")


# ============================================================================
# CHART 4: Engagement segmentation
# ============================================================================
fig, ax = plt.subplots(1, 1, figsize=(13, 5.5))

seg_data = results['engagement_segmentation']
tiers = list(seg_data.keys())
ret_30 = [seg_data[t]['ret7_gate_30'] * 100 for t in tiers]
ret_40 = [seg_data[t]['ret7_gate_40'] * 100 for t in tiers]
diffs = [seg_data[t]['abs_diff_pp'] for t in tiers]
sample_sizes = [seg_data[t]['n_total'] for t in tiers]

x = np.arange(len(tiers))
width = 0.35

bars1 = ax.bar(x - width/2, ret_30, width, label='gate_30', color=COLORS['gate_30'], 
              alpha=0.8, edgecolor='white', linewidth=1.5)
bars2 = ax.bar(x + width/2, ret_40, width, label='gate_40', color=COLORS['gate_40'],
              alpha=0.8, edgecolor='white', linewidth=1.5)

# Annotations
for i, (r30, r40, diff, n) in enumerate(zip(ret_30, ret_40, diffs, sample_sizes)):
    y_max = max(r30, r40)
    color = COLORS['gate_30'] if diff < 0 else COLORS['gate_40']
    ax.annotate(f'{diff:+.2f}pp', (i, y_max + 1.2), ha='center', 
               fontweight='bold', fontsize=10, color=color)

# Custom x-labels with n underneath
xlabels = [f'{t}\nn={n:,}' for t, n in zip(tiers, sample_sizes)]
ax.set_xticks(x)
ax.set_xticklabels(xlabels, fontsize=9)
ax.set_ylabel('7-Day Retention (%)')
ax.set_ylim(0, 38)
ax.set_title('Where the gate hurts most: engaged players (31-100 rounds) lose 1.27pp', loc='left')
ax.legend(loc='upper left', framealpha=0.95)

# Move callout to top center area where there's space
ax.text(0.5, 0.96,
       "Engaged players are the most sensitive to gate placement — and they're also the highest-LTV segment.",
       transform=ax.transAxes, ha='center', va='top', fontsize=10, style='italic',
       color='#374151',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF3C7', edgecolor='#F59E0B'))

plt.suptitle('Cookie Cats: 7-Day Retention by Engagement Segment',
            fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/home/claude/charts/CC_04_segmentation.png', dpi=140, bbox_inches='tight',
           facecolor='white')
plt.close()
print("✓ CC_04_segmentation.png")


# ============================================================================
# CHART 5: Decision summary (the signature view)
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(15, 9))

# Top-left: The headline numbers
ax = axes[0, 0]
ax.axis('off')

ax.text(0.5, 0.95, 'COOKIE CATS DECISION SUMMARY', ha='center', fontsize=14, 
       fontweight='bold', transform=ax.transAxes, color='#1F2937')

decision_box = (
    f"\nDecision: KEEP GATE AT LEVEL 30\n"
    f"Sample: 90,189 mobile game players\n"
    f"Confidence: HIGH (Bayesian P > 99%)"
)
ax.text(0.5, 0.6, decision_box, ha='center', va='center', fontsize=11,
       transform=ax.transAxes, linespacing=1.8,
       bbox=dict(boxstyle='round,pad=1', facecolor='#DBEAFE', edgecolor='#3B82F6', linewidth=2))

key_findings = (
    "• 1-day retention: not significantly different\n"
    "• 7-day retention: gate_30 is 0.83pp higher (p=0.003)\n"
    "• Bayesian P(gate_30 wins at D7): 99.86%\n"
    "• Effect concentrated in engaged players (highest LTV)"
)
ax.text(0.5, 0.18, key_findings, ha='center', va='center', fontsize=10,
       transform=ax.transAxes, linespacing=1.8, color='#374151')

# Top-right: Effect size with CI
ax = axes[0, 1]

metrics = ['1-day\nRetention', '7-day\nRetention']
diffs_pct = [results['retention_1_day']['absolute_diff_pp'], 
             results['retention_7_day']['absolute_diff_pp']]
ci_lower = [results['retention_1_day']['ci_95_pp'][0], 
            results['retention_7_day']['ci_95_pp'][0]]
ci_upper = [results['retention_1_day']['ci_95_pp'][1],
            results['retention_7_day']['ci_95_pp'][1]]

err_lower = [d - l for d, l in zip(diffs_pct, ci_lower)]
err_upper = [u - d for d, u in zip(diffs_pct, ci_upper)]

colors_err = [COLORS['neutral'], COLORS['gate_30']]
y_pos = np.arange(len(metrics))

ax.errorbar(diffs_pct, y_pos, xerr=[err_lower, err_upper], 
           fmt='o', markersize=12, color=COLORS['gate_30'],
           capsize=6, capthick=2, elinewidth=2,
           markeredgecolor='white', markeredgewidth=2)

ax.axvline(0, color='#6B7280', linestyle='--', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(metrics, fontsize=11)
ax.set_xlabel('Difference: gate_40 − gate_30 (percentage points)')
ax.set_title('Effect size with 95% CIs', loc='left')

for i, (d, l, u) in enumerate(zip(diffs_pct, ci_lower, ci_upper)):
    sig = '★ significant' if u < 0 else 'not significant'
    text_color = COLORS['gate_30'] if u < 0 else '#6B7280'
    # Place text below the error bar marker, not above
    ax.text(d, i - 0.25, f'Δ = {d:+.2f}pp  [{l:+.2f}, {u:+.2f}]\n{sig}',
           ha='center', va='top', fontsize=9, color=text_color,
           fontweight='bold' if u < 0 else 'normal')

ax.set_ylim(-0.7, 1.5)

# Bottom-left: Bayesian probabilities
ax = axes[1, 0]
labels = ['P(gate_30 better)\nat day 1', 'P(gate_30 better)\nat day 7', 
          'P(gate_40 hurts\nby ≥1pp at D7)']
probs = [results['bayesian']['d1_prob_gate30_better'],
         results['bayesian']['d7_prob_gate30_better'],
         results['bayesian']['d7_prob_gate40_loses_at_least_1pp']]
colors_p = [COLORS['neutral'], COLORS['gate_30'], COLORS['warning']]

bars = ax.barh(labels, probs, color=colors_p, alpha=0.8, edgecolor='white', linewidth=2, height=0.55)
for bar, p in zip(bars, probs):
    ax.text(bar.get_width() + 0.015, bar.get_y() + bar.get_height()/2,
           f'{p:.3f}', va='center', fontweight='bold', fontsize=11)

ax.axvline(0.95, color='#9CA3AF', linestyle='--', linewidth=1, label='95% threshold')
ax.set_xlim(0, 1.1)
ax.set_xlabel('Posterior Probability')
ax.set_title('Bayesian probabilities', loc='left')
ax.legend(loc='lower right', fontsize=9)

# Bottom-right: The business interpretation
ax = axes[1, 1]
ax.axis('off')

ax.text(0.05, 0.95, 'WHY THIS MATTERS', fontsize=12, fontweight='bold',
       transform=ax.transAxes, color='#1F2937')

explanation = (
    "The intuition would say: 'Less friction = better.\n"
    "Move the gate later, players will play more.'\n\n"
    "The data says the opposite. Why?\n\n"
    "The forced wait at level 30 likely creates a\n"
    "habit-forming pause. Players come back the next\n"
    "day to continue. Moving it to level 40 means\n"
    "more players hit the gate after they've already\n"
    "lost interest, rather than during peak engagement.\n\n"
    "The lesson: friction in the right place isn't bad.\n"
    "It can be the trigger for habit formation."
)
ax.text(0.05, 0.85, explanation, fontsize=10, va='top', ha='left',
       transform=ax.transAxes, linespacing=1.5, color='#374151')

plt.suptitle('Cookie Cats: A real-world A/B test where intuition is wrong',
            fontsize=15, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('/home/claude/charts/CC_05_decision.png', dpi=140, bbox_inches='tight',
           facecolor='white')
plt.close()
print("✓ CC_05_decision.png")

print("\nAll Cookie Cats visualizations complete.")
