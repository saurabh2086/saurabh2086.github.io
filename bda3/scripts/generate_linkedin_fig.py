"""
Generate high-resolution LinkedIn Graphic: Comparing Levels of Statistical Inference
BDA3 Chapter 8.3: 1988 Election Survey Case Study
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde

# 1. Load precomputed summary data
summary_path = "bda3/ch8/figures/hierarchical_shrinkage_summary.json"
with open(summary_path, "r") as f:
    data = json.load(f)

strata = data["strata"]
K = len(strata)

labels = [s["label"] for s in strata]
raw_vals = np.array([s["raw_bush_decided"] for s in strata])
hier_med = np.array([s["hier_med"] for s in strata])
hier_low = np.array([s["hier_low"] for s in strata])
hier_high = np.array([s["hier_high"] for s in strata])
n_vec = np.array([s["n"] for s in strata])
weights = np.array([s["weight_pct"] for s in strata])

# National grand mean among decided
grand_mean = 54.87

# Simulated posterior draws for national lead for smooth density
np.random.seed(42)
hier_lead_mean = data["hier_lead_decided"]["mean"]
hier_lead_std = (data["hier_lead_decided"]["hdi_97.5"] - data["hier_lead_decided"]["hdi_2.5"]) / 3.92
sim_hier_lead = np.random.normal(hier_lead_mean, hier_lead_std, 10000)

raw_lead_val = 9.75
nopool_lead_mean = data["nopool_lead_decided"]["mean"]
nopool_lead_std = (data["nopool_lead_decided"]["hdi_97.5"] - data["nopool_lead_decided"]["hdi_2.5"]) / 3.92
sim_nopool_lead = np.random.normal(nopool_lead_mean, nopool_lead_std, 10000)

# Set up figure styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

fig = plt.figure(figsize=(18, 10), dpi=300, facecolor='#f8fafc')

# Main title banner
fig.text(0.05, 0.95, "Levels of Statistical Inference: From Noisy Pockets to True Population Signals",
         fontsize=20, fontweight='bold', color='#0f172a')
fig.text(0.05, 0.92, "A Case Study in 1,447 Pre-Election Survey Interviews Across 16 Demographic Groups (Gelman et al., BDA3)",
         fontsize=13, color='#475569')

gs = gridspec.GridSpec(1, 2, width_ratios=[1.25, 0.95], wspace=0.28,
                       left=0.06, right=0.96, top=0.87, bottom=0.08)

# ==========================================
# PANEL A: Subgroup Inferences (16 Strata)
# ==========================================
ax_left = fig.add_subplot(gs[0])
ax_left.set_facecolor('#ffffff')

# Background region bands
regions = [
    ("Northeast (Strata 1–4)", 0, 3, '#eff6ff'),
    ("Midwest (Strata 5–8)", 4, 7, '#f8fafc'),
    ("South (Strata 9–12)", 8, 11, '#eff6ff'),
    ("West (Strata 13–16)", 12, 15, '#f8fafc')
]
for name, start, end, col in regions:
    ax_left.axhspan(start - 0.45, end + 0.45, color=col, alpha=0.7, zorder=0)

y_pos = np.arange(K)

# Complete Pooling vertical reference line
ax_left.axvline(grand_mean, color='#94a3b8', linestyle='--', linewidth=1.5, zorder=1,
                label=f'Level 2: Complete Pooling (Flat National Mean: {grand_mean:.1f}%)')

# Plot shrinkage arrows, credible intervals, and points
for i in range(K):
    # Error bar
    ax_left.plot([hier_low[i], hier_high[i]], [i, i], color='#2563eb', linewidth=2.5,
                 solid_capstyle='round', zorder=2, alpha=0.85)
    
    # Shrinkage arrow
    diff = hier_med[i] - raw_vals[i]
    if abs(diff) > 1.2:
        arrow_color = '#059669' if diff > 0 else '#dc2626'
        ax_left.annotate(
            '',
            xy=(hier_med[i], i),
            xytext=(raw_vals[i], i),
            arrowprops=dict(
                arrowstyle='->,head_width=0.25,head_length=0.4',
                color=arrow_color,
                lw=1.5,
                shrinkA=5,
                shrinkB=5,
                alpha=0.85
            ),
            zorder=3
        )
    
    # Raw isolated sample point
    ax_left.scatter(raw_vals[i], i, s=70, facecolors='#ffffff', edgecolors='#64748b',
                    linewidth=2.0, zorder=4, label='Level 1: Isolated Raw Sample' if i == 0 else "")
    
    # Connected Bayesian point
    ax_left.scatter(hier_med[i], i, s=80, color='#1e3a8a', edgecolors='#172554',
                    linewidth=1.2, zorder=5, label='Level 3: Connected Bayesian Shrinkage' if i == 0 else "")

# Callout annotation for Stratum 1 fluke
ax_left.annotate(
    "Rural Fluke (n=47):\nRaw 32.6% shrinks to 51.2%\n(+18.6 pt upward pull!)",
    xy=(hier_med[0], 0), xytext=(22, 1.3),
    arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5, connectionstyle="arc3,rad=-0.2"),
    fontsize=9.5, fontweight='bold', color="#065f46",
    bbox=dict(boxstyle="round,pad=0.4", fc="#ecfdf5", ec="#a7f3d0", lw=1)
)

# Callout annotation for Stratum 9 fluke
ax_left.annotate(
    "Small Cell Fluke (n=21):\nRaw 66.7% shrinks to 56.1%\n(-10.6 pt downward pull)",
    xy=(hier_med[8], 8), xytext=(68, 6.7),
    arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5, connectionstyle="arc3,rad=-0.2"),
    fontsize=9.5, fontweight='bold', color="#991b1b",
    bbox=dict(boxstyle="round,pad=0.4", fc="#fef2f2", ec="#fecaca", lw=1)
)

ax_left.set_yticks(y_pos)
ax_left.set_yticklabels(labels, fontsize=10, color='#1e293b')
ax_left.invert_yaxis()
ax_left.set_xlabel("Candidate Preference Share Among Decided Voters (%)", fontsize=11, fontweight='bold', color='#1e293b', labelpad=10)
ax_left.set_xlim(18, 80)
ax_left.grid(axis='x', color='#e2e8f0', linestyle=':', linewidth=1.0)
ax_left.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9.5)
ax_left.set_title("Panel A: Subgroup Level — Adaptive Shrinkage Tames Small-Sample Noise",
                  fontsize=12.5, fontweight='bold', color='#1e293b', pad=12)

# ==========================================
# RIGHT COLUMN: Two Subpanels (B and C)
# ==========================================
gs_right = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[1], hspace=0.35)

# ------------------------------------------
# PANEL B: Spread of Estimates Across Groups
# ------------------------------------------
ax_b = fig.add_subplot(gs_right[0])
ax_b.set_facecolor('#ffffff')

# Compare spread: Isolated vs Connected
y_scatter_raw = np.ones(K) * 1.0 + np.random.normal(0, 0.03, K)
y_scatter_hier = np.ones(K) * 0.0 + np.random.normal(0, 0.03, K)

ax_b.scatter(raw_vals, y_scatter_raw, s=75, facecolors='#ffffff', edgecolors='#dc2626',
             linewidth=2.0, alpha=0.9, label='Level 1: Isolated (Wild 34.1 pt range: 32.6% to 66.7%)')
ax_b.scatter(hier_med, y_scatter_hier, s=85, color='#1e3a8a', edgecolors='#172554',
             linewidth=1.2, alpha=0.9, label='Level 3: Connected (Coherent 7.9 pt range: 50.0% to 57.9%)')

# Annotate ranges with clean horizontal span bars
ax_b.hlines(1.35, raw_vals.min(), raw_vals.max(), colors='#dc2626', linewidth=2.0)
ax_b.text((raw_vals.min() + raw_vals.max()) / 2, 1.48, "34.1 pt Spread (High Noise / Low Trust)",
          ha='center', fontsize=9.2, fontweight='bold', color='#991b1b')

ax_b.hlines(-0.35, hier_med.min(), hier_med.max(), colors='#1e3a8a', linewidth=2.0)
ax_b.text((hier_med.min() + hier_med.max()) / 2, -0.48, "7.9 pt Spread (Shared Information)",
          ha='center', fontsize=9.2, fontweight='bold', color='#1e3a8a')

ax_b.set_yticks([0, 1])
ax_b.set_yticklabels(['Connected\n(Partial Pooling)', 'Isolated\n(No Pooling)'], fontsize=10, fontweight='bold', color='#1e293b')
ax_b.set_ylim(-0.95, 1.95)
ax_b.set_xlim(25, 75)
ax_b.grid(axis='x', color='#e2e8f0', linestyle=':', linewidth=1.0)
ax_b.set_xlabel("Candidate Preference (%)", fontsize=10.5, color='#475569')
ax_b.set_title("Panel B: Distributional Contraction Across 16 Subgroups",
               fontsize=12, fontweight='bold', color='#1e293b', pad=10)
ax_b.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5)

# ------------------------------------------
# PANEL C: National Outcome & The Paradox
# ------------------------------------------
ax_c = fig.add_subplot(gs_right[1])
ax_c.set_facecolor('#ffffff')

kde_hier = gaussian_kde(sim_hier_lead)
kde_nopool = gaussian_kde(sim_nopool_lead)
x_lead = np.linspace(2, 22, 400)

ax_c.plot(x_lead, kde_nopool(x_lead), color='#64748b', linestyle='--', linewidth=2.0,
          label='No-Pooling Poststratified Lead (Median: +11.1%)')
ax_c.plot(x_lead, kde_hier(x_lead), color='#059669', linewidth=2.5,
          label='Hierarchical Poststratified Lead (Median: +11.0%)')
ax_c.fill_between(x_lead, 0, kde_hier(x_lead), color='#10b981', alpha=0.18)

# Raw unweighted sample lead marker
ax_c.axvline(raw_lead_val, color='#d97706', linestyle='-', linewidth=2.2,
             label=f'Level 2: Raw Sample Total (+{raw_lead_val:.1f}%)')

# Callout explanation of the fluke paradox
ax_c.annotate(
    "The Counterintuitive Shift:\n"
    "Raw sample lead (+9.8%) expands to +11.0%!\n"
    "Why? Because rural anti-Bush flukes\n"
    "were heavily oversampled in telephone quotas.",
    xy=(hier_lead_mean, 0.08), xytext=(12.5, 0.11),
    arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5, connectionstyle="arc3,rad=-0.15"),
    fontsize=9.2, color="#065f46",
    bbox=dict(boxstyle="round,pad=0.45", fc="#f0fdf4", ec="#86efac", lw=1)
)

ax_c.set_xlabel("Nationwide Decided Voter Lead Margin (%)", fontsize=10.5, fontweight='bold', color='#1e293b', labelpad=8)
ax_c.set_ylabel("Posterior Density", fontsize=10.5, color='#475569')
ax_c.set_xlim(3, 20)
ax_c.set_ylim(0, 0.19)
ax_c.grid(axis='x', color='#e2e8f0', linestyle=':', linewidth=1.0)
ax_c.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.8)
ax_c.set_title("Panel C: National Level — Why Shrinkage Expands the Lead",
               fontsize=12, fontweight='bold', color='#1e293b', pad=10)

# Stylized border for all subplots
for ax in [ax_left, ax_b, ax_c]:
    for spine in ax.spines.values():
        spine.set_color('#cbd5e1')
        spine.set_linewidth(1.0)

out_fig_path = "bda3/ch8/figures/linkedin_inference_comparison.png"
plt.savefig(out_fig_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()

print(f"==> Successfully generated LinkedIn figure: {out_fig_path}")
