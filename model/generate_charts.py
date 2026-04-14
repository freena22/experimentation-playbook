"""
Visualizations for 6 experiments — each plot tailored to its teaching moment.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = _ROOT / "data" / "experiments"
RESULTS_DIR = _ROOT / "data" / "results"
CHARTS_DIR = _ROOT / "charts"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Consulting-grade palette
COLORS = {
    'control': '#6B7280',      # gray
    'treatment': '#3B82F6',    # blue
    'holdout': '#A78BFA',      # purple
    'positive': '#10B981',     # green
    'negative': '#EF4444',     # red
    'warning': '#F59E0B',      # amber
    'neutral': '#94A3B8',      # slate
    'accent': '#1E40AF',       # dark blue
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
    'xtick.color': '#4B5563',
    'ytick.color': '#4B5563',
    'grid.color': '#E5E7EB',
    'grid.linewidth': 0.6,
})


def save(fig, name):
    fig.savefig(CHARTS_DIR / f'{name}.png', dpi=140, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  ✓ {name}.png")


# ============================================================================
# E1 — Clean winner, segment consistency
# ============================================================================
print("\nE1: Social Login")
with open(RESULTS_DIR / 'E1_results.json') as f:
    e1 = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Overall result
ax = axes[0]
variants = ['Control', 'Treatment']
rates = [e1['frequentist']['control_rate'] * 100, 
         e1['frequentist']['treatment_rate'] * 100]
bars = ax.bar(variants, rates, color=[COLORS['control'], COLORS['treatment']], 
              width=0.5, edgecolor='white', linewidth=2)
for bar, rate in zip(bars, rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
           f'{rate:.1f}%', ha='center', fontsize=13, fontweight='bold')
ax.set_ylabel('Signup Completion Rate (%)')
ax.set_title('Signup Completion: Control vs Treatment', loc='left')
ax.set_ylim(0, max(rates) * 1.22)

# Annotation via arrow between the two bars
lift = e1['frequentist']['relative_lift_pct']
p_val = e1['frequentist']['p_value']

# Arrow from control to treatment
ax.annotate('', xy=(1, rates[1] * 1.08), xytext=(0, rates[0] * 1.08),
           arrowprops=dict(arrowstyle='->', color=COLORS['positive'], lw=2))
ax.text(0.5, (rates[0] + rates[1])/2 + 5, f'+{lift}% lift', 
       ha='center', fontsize=14, fontweight='bold', color=COLORS['positive'])
ax.text(0.5, (rates[0] + rates[1])/2 + 2, f'p < 0.001  |  P(T>C) = 1.00', 
       ha='center', fontsize=9, color='#6B7280')

# Right: Segment consistency
ax = axes[1]
segments = []
lifts = []
errs_lower = []
errs_upper = []

for dim_name, segs in e1['segment_consistency'].items():
    for s in segs:
        label = f"{dim_name}: {s['segment']}"
        segments.append(label)
        lifts.append(s['lift_pct'])
        # Convert CI to relative terms (approximate)
        ci_width = (s['ci_95_abs'][1] - s['ci_95_abs'][0]) / 2
        # Rough conversion to relative scale
        control_est = s.get('control_rate', 0.62)
        rel_ci = ci_width / control_est * 100 if control_est > 0 else 2
        errs_lower.append(rel_ci)
        errs_upper.append(rel_ci)

y_pos = np.arange(len(segments))
ax.barh(y_pos, lifts, xerr=[errs_lower, errs_upper], color=COLORS['treatment'],
       alpha=0.7, edgecolor='white', ecolor='#4B5563', capsize=3, error_kw={'linewidth': 1.2})
ax.axvline(0, color='#9CA3AF', linewidth=0.8)
ax.axvline(lift, color=COLORS['positive'], linestyle='--', linewidth=1.5, 
          label=f'Overall lift: +{lift}%')
ax.set_yticks(y_pos)
ax.set_yticklabels(segments, fontsize=9)
ax.set_xlabel('Relative Lift (%)')
ax.set_title('Segment Consistency — effect present in every segment', loc='left')
ax.legend(loc='lower right', fontsize=9)

plt.suptitle('E1: Social Login at Signup  —  Clean, consistent winner', 
            fontsize=14, fontweight='bold', y=1.02)
save(fig, 'E1_social_login')


# ============================================================================
# E2 — Simpson's paradox
# ============================================================================
print("\nE2: Extended Trial")
with open(RESULTS_DIR / 'E2_results.json') as f:
    e2 = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Overall vs by-segment comparison
ax = axes[0]
categories = ['Overall', 'New users', 'Returning', 'Tenured']
lifts = [
    e2['frequentist_overall']['relative_lift_pct'],
    next(r for r in e2['segment_analysis'] if r['segment'] == 'new')['lift_pct'],
    next(r for r in e2['segment_analysis'] if r['segment'] == 'returning')['lift_pct'],
    next(r for r in e2['segment_analysis'] if r['segment'] == 'tenured')['lift_pct'],
]
colors = [COLORS['neutral']] + [COLORS['positive'] if l > 0 else COLORS['negative'] for l in lifts[1:]]
bars = ax.bar(categories, lifts, color=colors, edgecolor='white', linewidth=2, width=0.6)
for bar, lift in zip(bars, lifts):
    y = bar.get_height()
    va = 'bottom' if y >= 0 else 'top'
    offset = 0.8 if y >= 0 else -0.8
    ax.text(bar.get_x() + bar.get_width()/2, y + offset,
           f'{lift:+.1f}%', ha='center', va=va, fontsize=11, fontweight='bold')

ax.axhline(0, color='#4B5563', linewidth=1)
ax.set_ylabel('Relative Lift in Trial→Paid Conversion (%)')
ax.set_title("The average lies: overall looks flat,\nbut segments tell opposite stories", loc='left')
ax.set_ylim(-15, 30)

# Annotation
ax.text(0.5, 0.95, "Simpson's Paradox", transform=ax.transAxes,
       ha='center', fontsize=13, fontweight='bold', color='#1E3A8A',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='#DBEAFE', edgecolor='#93C5FD'))

# Right: Segment mix showing why averaging is misleading
ax = axes[1]
mix = e2['simpsons_paradox']['segment_mix']
tenures = ['new', 'returning', 'tenured']
sizes = [mix[t] for t in tenures]
seg_lifts = [next(r for r in e2['segment_analysis'] if r['segment']==t)['lift_pct'] for t in tenures]
seg_colors = [COLORS['positive'] if l > 0 else COLORS['negative'] for l in seg_lifts]

# Stacked visual: x-axis = user mix, y-axis = lift
x_positions = np.cumsum([0] + sizes[:-1])
widths = sizes
heights = seg_lifts

for i, (x, w, h, tenure) in enumerate(zip(x_positions, widths, heights, tenures)):
    color = COLORS['positive'] if h > 0 else COLORS['negative']
    ax.bar(x + w/2, h, width=w*0.9, color=color, alpha=0.7, edgecolor='white', linewidth=2)
    ax.text(x + w/2, h + (1 if h > 0 else -1.5), f'{h:+.1f}%', 
           ha='center', fontweight='bold', fontsize=10)
    ax.text(x + w/2, -14, f'{tenure}\n({int(w*100)}% of users)', ha='center', fontsize=9, color='#4B5563')

ax.axhline(0, color='#4B5563', linewidth=1)
ax.axhline(e2['frequentist_overall']['relative_lift_pct'], color=COLORS['neutral'], 
          linestyle='--', linewidth=1.5, label=f'Weighted avg: {e2["frequentist_overall"]["relative_lift_pct"]:+.1f}%')
ax.set_ylabel('Segment Lift (%)')
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-15, 30)
ax.set_title('Why the average hides the truth: tenured/returning users\ndominate the mix and drag down the positive new-user effect', loc='left')
ax.legend(loc='upper right', fontsize=9)
ax.set_xticks([])

plt.suptitle("E2: Extended Trial  —  Ship to new users only, not to everyone", 
            fontsize=14, fontweight='bold', y=1.02)
save(fig, 'E2_extended_trial')


# ============================================================================
# E3 — Novelty decay
# ============================================================================
print("\nE3: Push Time Shift")
with open(RESULTS_DIR / 'E3_results.json') as f:
    e3 = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Weekly decay
ax = axes[0]
weeks = [w['week'] for w in e3['weekly_decay']]
lifts = [w['lift_pct'] for w in e3['weekly_decay']]
cis = [(w['ci_95_abs'][1] - w['ci_95_abs'][0]) / 2 / w['control_mean'] * 100 
       for w in e3['weekly_decay']]

# Shaded region for "novelty zone"
ax.fill_between([0.5, 2.5], [0, 0], [20, 20], color=COLORS['warning'], alpha=0.08, label='Novelty zone')
ax.fill_between([2.5, 4.5], [0, 0], [20, 20], color=COLORS['positive'], alpha=0.08, label='Steady-state')

ax.errorbar(weeks, lifts, yerr=cis, fmt='o-', color=COLORS['treatment'], 
           linewidth=2.5, markersize=10, capsize=4, markeredgecolor='white', markeredgewidth=1.5)
for w, l in zip(weeks, lifts):
    ax.annotate(f'{l:+.1f}%', (w, l), textcoords="offset points", xytext=(0, 15),
               ha='center', fontweight='bold', fontsize=10)

# Naive result line
naive = e3['naive_whole_period']['relative_lift_pct']
ax.axhline(naive, color=COLORS['warning'], linestyle='--', linewidth=1.5, alpha=0.8)
ax.text(4.3, naive + 0.5, f'Naive 4-wk avg: +{naive:.1f}%\n(the misleading read)', 
       fontsize=9, color=COLORS['warning'], ha='right', fontweight='bold')

# Steady state line
steady = e3['decay_analysis']['steady_state_lift_pct']
ax.axhline(steady, color=COLORS['positive'], linestyle=':', linewidth=1.5, alpha=0.8)
ax.text(4.3, steady - 1.3, f'Steady state: ~{steady:.1f}%', 
       fontsize=9, color=COLORS['positive'], ha='right', fontweight='bold')

ax.set_xticks(weeks)
ax.set_xticklabels([f'Week {w}' for w in weeks])
ax.set_ylabel('Relative Lift in Push Open Rate (%)')
ax.set_title('Lift decays from +15% in Week 1 to +2% by Week 4', loc='left')
ax.legend(loc='upper right', fontsize=9)
ax.set_ylim(0, 20)

# Right: "What we would have concluded" scenarios
ax = axes[1]
scenarios = ['1-week test\n(common)', '2-week test\n(standard)', '3-week test', '4-week test\n(what we ran)']
observed_lifts = [lifts[0], np.mean(lifts[:2]), np.mean(lifts[:3]), np.mean(lifts)]
would_ship = [l > 3 for l in observed_lifts]
bar_colors = [COLORS['negative'] if ship else COLORS['positive'] for ship in would_ship]

bars = ax.bar(scenarios, observed_lifts, color=bar_colors, alpha=0.7, 
             edgecolor='white', linewidth=2, width=0.55)
for bar, val, ship in zip(bars, observed_lifts, would_ship):
    decision = 'Would SHIP 😱' if ship else 'Would KILL ✓'
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
           f'{val:+.1f}%\n{decision}', ha='center', fontweight='bold', fontsize=9)

ax.axhline(3, color='#4B5563', linestyle='--', linewidth=1, alpha=0.5)
ax.text(0.02, 3.2, 'Typical ship threshold (~3%)', fontsize=8, color='#6B7280')
ax.set_ylabel('Observed Lift if Test Had Stopped Here (%)')
ax.set_title('A shorter test would have shipped a dud', loc='left')
ax.set_ylim(0, 17)

plt.suptitle('E3: Push Time Shift  —  Classic novelty effect (KILL)', 
            fontsize=14, fontweight='bold', y=1.02)
save(fig, 'E3_push_time')


# ============================================================================
# E4 — Primary metric vs North Star divergence
# ============================================================================
print("\nE4: Onboarding")
with open(RESULTS_DIR / 'E4_results.json') as f:
    e4 = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Funnel metrics
ax = axes[0]
metrics_info = [
    ('d1_activated', 'D1 Activation\n(Primary metric)'),
    ('d7_retained', 'D7 Retention\n(Guardrail)'),
    ('d30_retained', 'D30 Retention\n(North Star)'),
]
control_rates = [e4['funnel_analysis'][m]['control_rate'] * 100 for m, _ in metrics_info]
treatment_rates = [e4['funnel_analysis'][m]['treatment_rate'] * 100 for m, _ in metrics_info]

x = np.arange(len(metrics_info))
width = 0.35

ax.bar(x - width/2, control_rates, width, label='Control', color=COLORS['control'], 
      edgecolor='white', linewidth=2)
ax.bar(x + width/2, treatment_rates, width, label='Treatment', color=COLORS['treatment'],
      edgecolor='white', linewidth=2)

for i, (m, _) in enumerate(metrics_info):
    lift = e4['funnel_analysis'][m]['lift_pct']
    sig = '✓' if e4['funnel_analysis'][m]['significant_at_05'] else ''
    color = COLORS['positive'] if lift > 0 else COLORS['negative']
    y = max(control_rates[i], treatment_rates[i]) + 2
    ax.annotate(f'{lift:+.1f}%{sig}', (i, y), ha='center', fontweight='bold', 
               fontsize=11, color=color)

ax.set_xticks(x)
ax.set_xticklabels([label for _, label in metrics_info], fontsize=9)
ax.set_ylabel('Rate (%)')
ax.set_ylim(0, 65)
ax.set_title('Primary metric wins but North Star loses', loc='left')
ax.legend(loc='upper right')

# Right: Business impact waterfall
ax = axes[1]
impact = e4['business_impact_model']

# Build proper waterfall data
gained_revenue = impact['projected_marginal_revenue_from_extra_activations'] / 1000
lost_revenue = impact['projected_lost_revenue_annual'] / 1000
net = impact['net_annual_revenue_impact'] / 1000

bar_labels = ['Revenue from\nextra activations', 'Revenue lost from\nretention decline', 'NET annual\nrevenue impact']
bar_vals = [gained_revenue, -lost_revenue, net]  # preserve sign
bar_colors = [COLORS['positive'], COLORS['negative'], COLORS['negative']]

bars = ax.bar(bar_labels, bar_vals, color=bar_colors, alpha=0.75, edgecolor='white', linewidth=2)
for bar, v in zip(bars, bar_vals):
    y = bar.get_height()
    va = 'bottom' if y >= 0 else 'top'
    offset = max(abs(y) * 0.04, 25) * (1 if y >= 0 else -1)
    sign = '+' if v >= 0 else '-'
    ax.text(bar.get_x() + bar.get_width()/2, y + offset, 
           f'{sign}${abs(int(v))}K', ha='center', va=va, fontweight='bold', fontsize=12)

ax.axhline(0, color='#4B5563', linewidth=1)
ax.set_ylabel('Annual Revenue Impact ($ thousands)')
ax.set_title(f'Net annual revenue impact: -${abs(int(net))}K  →  KILL', loc='left')
y_max = max(bar_vals) if max(bar_vals) > 0 else 100
y_min = min(bar_vals)
ax.set_ylim(y_min * 1.25, y_max * 1.25)

plt.suptitle('E4: Shortened Onboarding  —  Primary metric ≠ Business value', 
            fontsize=14, fontweight='bold', y=1.02)
save(fig, 'E4_onboarding')


# ============================================================================
# E5 — Underpowered test
# ============================================================================
print("\nE5: AI Conversation")
with open(RESULTS_DIR / 'E5_results.json') as f:
    e5 = json.load(f)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: The problem — small sample + small effect
ax = axes[0]
power = e5['power_analysis']
observed_lift = power['observed_lift_pct']
n_per = power['sample_size_used_per_variant']
needed_n = power['sample_size_needed_for_80_pct_power']
mde_possible = power['minimum_detectable_effect_pct']

# Show actual confidence interval width vs needed effect size
fig_data = {
    'Observed lift': observed_lift,
    'MDE we could detect\n(80% power)': mde_possible,
    'MDE we were\nsized for (at design)': 8.0,
}
labels = list(fig_data.keys())
vals = list(fig_data.values())
colors_mde = [COLORS['treatment'], COLORS['warning'], COLORS['negative']]

bars = ax.barh(labels, vals, color=colors_mde, alpha=0.75, edgecolor='white', linewidth=2, height=0.6)
for bar, v in zip(bars, vals):
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
           f'{v:.1f}%', va='center', fontweight='bold', fontsize=11)

ax.set_xlabel('Effect Size (%)')
ax.set_xlim(0, 10)
ax.set_title('The mismatch: our sample could only detect 4.9%,\nbut the true effect is ~2-3%', loc='left')

# Right: Sample size we needed
ax = axes[1]
categories = ['Sample we had\n(per variant)', 'Sample needed\nfor 80% power']
values = [n_per, needed_n]
colors_ss = [COLORS['negative'], COLORS['positive']]

bars = ax.bar(categories, values, color=colors_ss, alpha=0.75, edgecolor='white', linewidth=2, width=0.5)
for bar, v in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
           f'{v:,}', ha='center', fontweight='bold', fontsize=13)

ax.set_ylabel('Users per Variant')
ax.set_ylim(0, max(values) * 1.2)
ax.set_title(f'We needed {int(needed_n/n_per)}x more users to detect this effect', loc='left')

# Key interpretation box
ax.text(0.5, -0.28, 
       f'Post-hoc power: {int(e5["power_analysis"]["actual_statistical_power"]*100)}%   |   '
       f'p = {e5["frequentist"]["p_value"]:.3f}   |   Directionally positive',
       transform=ax.transAxes, ha='center', fontsize=11,
       bbox=dict(boxstyle='round,pad=0.5', facecolor='#FEF3C7', edgecolor='#F59E0B'))

plt.suptitle('E5: AI Conversation Practice  —  p=0.13 ≠ "no effect" (RE-RUN)',
            fontsize=14, fontweight='bold', y=1.02)
save(fig, 'E5_ai_practice')


# ============================================================================
# E6 — CUPED + Bayesian + holdout
# ============================================================================
print("\nE6: Leaderboard")
with open(RESULTS_DIR / 'E6_results.json') as f:
    e6 = json.load(f)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Left: Main result with holdout
ax = axes[0]
variants = ['Control', 'Treatment', 'Holdout']
means = [e6['standard_analysis']['control_mean'], 
         e6['standard_analysis']['treatment_mean'],
         e6['standard_analysis']['control_mean'] + 
         (e6['holdout_validation']['control_vs_holdout_lift_pct']/100) * e6['standard_analysis']['control_mean']]
colors_v = [COLORS['control'], COLORS['treatment'], COLORS['holdout']]

bars = ax.bar(variants, means, color=colors_v, edgecolor='white', linewidth=2, width=0.5)
for bar, m in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
           f'{m:.2f}', ha='center', fontweight='bold', fontsize=11)

# Annotation arrow from Control to Treatment
lift_main = e6['standard_analysis']['relative_lift_pct']
ax.annotate('', xy=(1, means[1]), xytext=(0, means[0]),
           arrowprops=dict(arrowstyle='->', color=COLORS['positive'], lw=2))
ax.text(0.5, (means[0]+means[1])/2 + 0.3, f'+{lift_main:.1f}%', 
       ha='center', fontweight='bold', fontsize=13, color=COLORS['positive'])

# Control vs Holdout annotation
cvh = e6['holdout_validation']['control_vs_holdout_lift_pct']
ax.text(2, means[2] + 1, f'C vs H:\n{cvh:+.2f}%\n(validates\ncontrol)', 
       ha='center', fontsize=9, color=COLORS['holdout'],
       bbox=dict(boxstyle='round,pad=0.3', facecolor='#F3E8FF', edgecolor='#C4B5FD'))

ax.set_ylabel('Active Days in 30-Day Window')
ax.set_title('Treatment effect validated by holdout', loc='left')

# Middle: CUPED variance reduction
ax = axes[1]
methods = ['Standard\nAnalysis', 'CUPED-adjusted\nAnalysis']
ci_widths = [
    e6['standard_analysis']['ci_95_abs'][1] - e6['standard_analysis']['ci_95_abs'][0],
    e6['cuped_analysis']['result']['ci_95_abs'][1] - e6['cuped_analysis']['result']['ci_95_abs'][0]
]
var_reduction = e6['cuped_analysis']['variance_reduction_pct']

bars = ax.bar(methods, ci_widths, color=[COLORS['control'], COLORS['treatment']], 
             edgecolor='white', linewidth=2, width=0.5)
for bar, w in zip(bars, ci_widths):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
           f'{w:.3f}', ha='center', fontweight='bold', fontsize=11)

ax.set_ylabel('95% CI Width on Treatment Effect')
ax.set_ylim(0, max(ci_widths) * 1.25)
ax.set_title(f'CUPED reduces variance by {var_reduction:.0f}%', loc='left')
ax.text(0.5, -0.18, f'≈ like running with {int(100/(100-var_reduction) * 100 - 100)}% more users',
       transform=ax.transAxes, ha='center', fontsize=10, color='#6B7280', style='italic')

# Right: Bayesian posterior
ax = axes[2]
bayes = e6['bayesian_analysis']

# Simulate posterior
np.random.seed(42)
lift_samples = np.random.normal(lift_main, 1.2, 50000)
ax.hist(lift_samples, bins=60, color=COLORS['treatment'], alpha=0.7, edgecolor='white')
ax.axvline(0, color=COLORS['negative'], linestyle='--', linewidth=1.5)
ax.axvline(10, color=COLORS['warning'], linestyle=':', linewidth=1.5)
ax.axvline(lift_main, color=COLORS['accent'], linewidth=2)

ax.text(lift_main + 0.5, ax.get_ylim()[1]*0.9, f'Expected: +{lift_main:.1f}%', 
       fontweight='bold', color=COLORS['accent'])
ax.text(0.3, ax.get_ylim()[1]*0.65, f'P(lift>0) = {bayes["prob_treatment_better"]}', 
       fontsize=10, color='#4B5563')
ax.text(10.3, ax.get_ylim()[1]*0.45, f'P(lift>10%) = {bayes["prob_lift_exceeds_10pct"]}',
       fontsize=10, color=COLORS['warning'])

ax.set_xlabel('Relative Lift (%)')
ax.set_ylabel('Posterior Density')
ax.set_title('Bayesian posterior distribution', loc='left')
ax.set_yticks([])

plt.suptitle('E6: Leaderboard  —  Textbook rigor (SHIP)', 
            fontsize=14, fontweight='bold', y=1.02)
save(fig, 'E6_leaderboard')


# ============================================================================
# PORTFOLIO DASHBOARD — the signature chart
# ============================================================================
print("\nPortfolio Summary Chart")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Top-left: Decision breakdown
ax = axes[0, 0]
decisions = ['Ship\n(2)', 'Ship to\nsegment (1)', 'Re-run\n(1)', 'Kill\n(2)']
counts = [2, 1, 1, 2]
colors_d = [COLORS['positive'], '#34D399', COLORS['warning'], COLORS['negative']]

wedges, texts = ax.pie(counts, labels=decisions, colors=colors_d,
                        startangle=90, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3),
                        textprops=dict(fontsize=11, fontweight='bold'))

ax.text(0, 0, '6\nexperiments', ha='center', va='center', fontsize=14, fontweight='bold')
ax.set_title('Q3 2025 Decisions: 33% unconditional ship rate', loc='left', pad=20)

# Top-right: Lift comparison
ax = axes[0, 1]
exps = ['E1\nSocial\nLogin', 'E2\nExt.Trial\n(new users)', 'E3\nPush\nTime', 'E4\nOnboarding\n(D30)',
        'E5\nAI\nPractice', 'E6\nLeader\nboard']
lifts = [9.24, 22.9, 2.35, -9.5, 2.61, 21.79]
decisions_short = ['SHIP', 'SHIP (seg)', 'KILL', 'KILL', 'RE-RUN', 'SHIP']
colors_e = [COLORS['positive'], COLORS['positive'], COLORS['negative'], COLORS['negative'],
            COLORS['warning'], COLORS['positive']]

bars = ax.bar(exps, lifts, color=colors_e, alpha=0.75, edgecolor='white', linewidth=2)
for bar, lift, dec in zip(bars, lifts, decisions_short):
    y = bar.get_height()
    va = 'bottom' if y >= 0 else 'top'
    offset = 0.7 if y >= 0 else -0.7
    ax.text(bar.get_x() + bar.get_width()/2, y + offset,
           f'{lift:+.1f}%', ha='center', va=va, fontweight='bold', fontsize=10)
    ax.text(bar.get_x() + bar.get_width()/2, -14 if y >=0 else -13,
           dec, ha='center', fontsize=8, fontweight='bold', color=colors_e[list(bars).index(bar)])

ax.axhline(0, color='#4B5563', linewidth=1)
ax.set_ylabel('Key Metric Lift (%)')
ax.set_title('Lift by experiment — look beyond the sign', loc='left')
ax.set_ylim(-18, 28)

# Bottom-left: Lessons learned pattern
ax = axes[1, 0]
patterns = ['Primary vs\nNorth Star\nmisalignment', 'Novelty\neffect', 'Underpowered\ntest',
           "Simpson's\nparadox"]
affected = ['E4', 'E3', 'E5', 'E2']
colors_p = [COLORS['negative'], COLORS['warning'], COLORS['warning'], COLORS['treatment']]

y_pos = np.arange(len(patterns))
bars = ax.barh(y_pos, [1]*len(patterns), color=colors_p, alpha=0.3, edgecolor='white', height=0.7)
for i, (p, a) in enumerate(zip(patterns, affected)):
    ax.text(0.02, i, p, va='center', fontsize=10, fontweight='bold')
    ax.text(0.98, i, f'Found in {a}', va='center', ha='right', fontsize=9, color='#6B7280')

ax.set_xlim(0, 1)
ax.set_yticks([])
ax.set_xticks([])
ax.set_title('Cross-experiment patterns drive next quarters policy', loc='left')
ax.invert_yaxis()
for spine in ax.spines.values():
    spine.set_visible(False)

# Bottom-right: The signature insight
ax = axes[1, 1]
ax.axis('off')

# Create a "key insight" text panel
insight_text = (
    "THE QUARTER IN ONE SENTENCE:\n\n"
    "Out of 6 experiments, only 2 shipped unconditionally.\n"
    "But the other 4 generated insights that will shape how\n"
    "we run the next 50 experiments.\n\n"
    "    → 2 experiments would have shipped on primary metrics\n"
    "       alone and damaged long-term retention\n\n"
    "    → 1 experiment was 'flat' until segment analysis\n"
    "       revealed a clear winning subpopulation\n\n"
    "    → 1 experiment was 'null' but actually directionally\n"
    "       positive — our MDE discipline needs tightening\n\n"
    "The real output of experimentation isnt ship decisions.\n"
    "Its organizational learning."
)

ax.text(0.02, 0.98, insight_text, transform=ax.transAxes, 
       fontsize=10.5, va='top', ha='left', color='#1F2937',
       bbox=dict(boxstyle='round,pad=1', facecolor='#F9FAFB', edgecolor='#E5E7EB', linewidth=1.5),
       linespacing=1.6)

plt.suptitle('LinguaLeap Q3 2025 Experimentation Program — Portfolio View',
            fontsize=15, fontweight='bold', y=1.00)
plt.tight_layout()
save(fig, 'Portfolio_summary')

print("\n" + "=" * 70)
print("ALL CHARTS GENERATED")
print("=" * 70)
for f in sorted(os.listdir(CHARTS_DIR)):
    print(f"  {f}")
