import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde
import pymc as pm
import arviz as az

counts = np.array([
    [14, 29, 4],    # 1: Northeast I
    [23, 22, 1],    # 2: Northeast II
    [78, 69, 20],   # 3: Northeast III
    [32, 36, 1],    # 4: Northeast IV
    [19, 23, 5],    # 5: Midwest I
    [42, 42, 10],   # 6: Midwest II
    [59, 45, 12],   # 7: Midwest III
    [80, 49, 16],   # 8: Midwest IV
    [12, 6, 3],     # 9: South I
    [45, 39, 12],   # 10: South II
    [51, 40, 8],    # 11: South III
    [101, 64, 17],  # 12: South IV
    [17, 16, 1],    # 13: West I
    [41, 27, 9],    # 14: West II
    [67, 46, 11],   # 15: West III
    [46, 30, 7]     # 16: West IV
])

strata_labels = [
    "1. Northeast I (Rural)",
    "2. Northeast II",
    "3. Northeast III",
    "4. Northeast IV (Urban)",
    "5. Midwest I (Rural)",
    "6. Midwest II",
    "7. Midwest III",
    "8. Midwest IV (Urban)",
    "9. South I (Rural)",
    "10. South II",
    "11. South III",
    "12. South IV (Urban)",
    "13. West I (Rural)",
    "14. West II",
    "15. West III",
    "16. West IV (Urban)"
]

n_vec = counts.sum(axis=1)
raw_bush_decided = counts[:, 0] / (counts[:, 0] + counts[:, 1])

W = np.array([
    0.032, 0.032, 0.115, 0.048,
    0.032, 0.065, 0.080, 0.100,
    0.015, 0.066, 0.068, 0.126,
    0.023, 0.053, 0.086, 0.057
])
W_norm = W / W.sum()

# 1. Fit Hierarchical Model
print("Fitting Hierarchical Model...")
with pm.Model() as model_hier:
    mu = pm.Normal("mu", mu=0.0, sigma=2.0, shape=2)
    chol, corr, sigmas = pm.LKJCholeskyCov(
        "chol_cov", n=2, eta=2.0, sd_dist=pm.HalfNormal.dist(sigma=1.0), compute_corr=True
    )
    z = pm.Normal("z", mu=0.0, sigma=1.0, shape=(16, 2))
    beta = pm.Deterministic("beta", mu + pm.math.dot(z, chol.T))
    
    alpha_1 = pm.Deterministic("alpha_1", pm.math.invlogit(beta[:, 0]))
    alpha_2 = pm.Deterministic("alpha_2", pm.math.invlogit(beta[:, 1]))
    
    theta_1 = pm.Deterministic("theta_1", alpha_1 * alpha_2)
    theta_2 = pm.Deterministic("theta_2", (1.0 - alpha_1) * alpha_2)
    theta_3 = pm.Deterministic("theta_3", 1.0 - alpha_2)
    theta = pm.Deterministic("theta", pm.math.stack([theta_1, theta_2, theta_3], axis=-1))
    
    obs = pm.Multinomial("obs", n=n_vec, p=theta, observed=counts)
    
    national_bush = pm.Deterministic("national_bush", pm.math.dot(W_norm, theta_1))
    national_dukakis = pm.Deterministic("national_dukakis", pm.math.dot(W_norm, theta_2))
    national_lead = pm.Deterministic("national_lead", national_bush - national_dukakis)
    national_alpha1 = pm.Deterministic("national_alpha1", national_bush / (national_bush + national_dukakis))
    
    idata_hier = pm.sample(draws=2500, tune=1500, chains=4, random_seed=42, target_accept=0.95)

# 2. Fit No-Pooling Corrected Model for comparison
print("Fitting No-Pooling Model...")
with pm.Model() as model_nopool:
    a_corrected = np.full((16, 3), 1.0 / 16.0)
    theta_np = pm.Dirichlet("theta_np", a=a_corrected, shape=(16, 3))
    obs_np = pm.Multinomial("obs_np", n=n_vec, p=theta_np, observed=counts)
    
    national_bush_np = pm.Deterministic("national_bush_np", pm.math.dot(W_norm, theta_np[:, 0]))
    national_duk_np = pm.Deterministic("national_duk_np", pm.math.dot(W_norm, theta_np[:, 1]))
    national_lead_np = pm.Deterministic("national_lead_np", national_bush_np - national_duk_np)
    
    idata_nopool = pm.sample(draws=2500, tune=1500, chains=4, random_seed=42, target_accept=0.9)

# 3. Extract Statistics
alpha1_draws = idata_hier.posterior["alpha_1"].values.reshape(-1, 16)

# Lead among decided voters: 2 * alpha_1 - 1
hier_alpha1_nat = idata_hier.posterior["national_alpha1"].values.flatten()
hier_lead = (2.0 * hier_alpha1_nat - 1.0) * 100

b_np = idata_nopool.posterior["national_bush_np"].values.flatten()
d_np = idata_nopool.posterior["national_duk_np"].values.flatten()
nopool_alpha1_nat = b_np / (b_np + d_np)
nopool_lead = (2.0 * nopool_alpha1_nat - 1.0) * 100

hier_meds = np.median(alpha1_draws, axis=0)
hier_low = np.percentile(alpha1_draws, 2.5, axis=0)
hier_high = np.percentile(alpha1_draws, 97.5, axis=0)

strata_results = []
for j in range(16):
    strata_results.append({
        "stratum": j + 1,
        "label": strata_labels[j],
        "n": int(n_vec[j]),
        "weight_pct": float(W[j] * 100),
        "raw_bush_decided": float(raw_bush_decided[j] * 100),
        "hier_med": float(hier_meds[j] * 100),
        "hier_low": float(hier_low[j] * 100),
        "hier_high": float(hier_high[j] * 100)
    })

os.makedirs("bda3/ch8/figures", exist_ok=True)
with open("bda3/ch8/figures/hierarchical_shrinkage_summary.json", "w") as f:
    json.dump({
        "strata": strata_results,
        "hier_lead_decided": {
            "median": float(np.median(hier_lead)),
            "mean": float(np.mean(hier_lead)),
            "hdi_2.5": float(np.percentile(hier_lead, 2.5)),
            "hdi_97.5": float(np.percentile(hier_lead, 97.5))
        },
        "nopool_lead_decided": {
            "median": float(np.median(nopool_lead)),
            "mean": float(np.mean(nopool_lead)),
            "hdi_2.5": float(np.percentile(nopool_lead, 2.5)),
            "hdi_97.5": float(np.percentile(nopool_lead, 97.5))
        }
    }, f, indent=2)

print("Data saved to JSON. Now generating Figure 8.4...")

# 4. Publication Plot: Figure 8.4
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
fig = plt.figure(figsize=(15, 9.5), dpi=300)
gs = gridspec.GridSpec(1, 2, width_ratios=[1.4, 1.0], wspace=0.30)

# Left Panel: 16 Strata Shrinkage Forest Plot
ax1 = fig.add_subplot(gs[0])
y_pos = np.arange(16)[::-1]  # Stratum 1 at top

nat_mean_decided = float(np.mean(idata_hier.posterior["national_alpha1"].values)) * 100

for j in range(16):
    y = y_pos[j]
    raw_val = raw_bush_decided[j] * 100
    post_val = hier_meds[j] * 100
    low_val = hier_low[j] * 100
    high_val = hier_high[j] * 100
    
    # 95% Credible Interval Bar
    ax1.plot([low_val, high_val], [y, y], color="#0284c7", lw=2.6, alpha=0.9, zorder=3)
    
    # Shrinkage Arrow from Raw -> Posterior Median
    # If arrow is very short, keep small
    delta = post_val - raw_val
    if abs(delta) > 1.2:
        ax1.annotate(
            "",
            xy=(post_val, y),
            xytext=(raw_val, y),
            arrowprops=dict(
                arrowstyle="->,head_width=0.25,head_length=0.35",
                color="#e11d48" if delta > 0 else "#2563eb",
                lw=1.5,
                alpha=0.75
            ),
            zorder=4
        )
    
    # Raw Point (Hollow / grey circle)
    ax1.scatter(raw_val, y, facecolors="#ffffff", edgecolors="#64748b", s=45, linewidth=1.4, zorder=5,
                label="Raw Sample Share" if j == 0 else "")
    
    # Posterior Median Point (Solid blue circle)
    ax1.scatter(post_val, y, color="#0284c7", s=55, edgecolor="white", linewidth=0.9, zorder=6,
                label="Hierarchical Posterior Median" if j == 0 else "")
    
    # Sample size label on the right
    ax1.text(78.5, y, f"n={n_vec[j]}", va="center", ha="left", fontsize=9, color="#64748b", family="sans-serif")

# Highlights for extreme strata 1, 5, 9
ax1.axhspan(y_pos[0] - 0.4, y_pos[0] + 0.4, color="#fef2f2", alpha=0.6, zorder=1)
ax1.axhspan(y_pos[4] - 0.4, y_pos[4] + 0.4, color="#fef2f2", alpha=0.6, zorder=1)
ax1.axhspan(y_pos[8] - 0.4, y_pos[8] + 0.4, color="#eff6ff", alpha=0.6, zorder=1)

# National Bush Reference Line
ax1.axvline(nat_mean_decided, color="#0f172a", linestyle="--", lw=1.3, alpha=0.75, zorder=2)
ax1.text(nat_mean_decided + 0.6, -0.7, f"National Mean: {nat_mean_decided:.1f}%", fontsize=8.5, color="#0f172a", fontweight="bold")

ax1.set_yticks(y_pos)
ax1.set_yticklabels([strata_labels[j] for j in range(16)], fontsize=9.5)
ax1.set_xlabel("Bush Share Among Decided Voters: $\\alpha_{1j}$ (%)", fontsize=11, fontweight="bold", labelpad=8)
ax1.set_xlim(22, 88)
ax1.set_title("A. Hierarchical Shrinkage Across 16 Strata\n(Arrows show pull from raw data $\\hat{\\alpha}_{1j}$ to posterior $\\alpha_{1j}$)",
              fontsize=12, fontweight="bold", pad=12, loc="left")
ax1.legend(loc="lower left", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.95)
ax1.grid(True, linestyle=":", alpha=0.6)

# Right Panel: National Poststratified Lead Comparison
ax2 = fig.add_subplot(gs[1])

x_grid = np.linspace(-2, 22, 600)
kde_hier = gaussian_kde(hier_lead)(x_grid)
kde_np = gaussian_kde(nopool_lead)(x_grid)

# No Pooling Density (Grey / Dashed)
ax2.plot(x_grid, kde_np, color="#64748b", lw=2.0, linestyle="--",
         label=f"No Pooling (Table 8.2)\nMedian: +{np.median(nopool_lead):.1f}% [{np.percentile(nopool_lead, 2.5):.1f}%, {np.percentile(nopool_lead, 97.5):.1f}%]")
ax2.fill_between(x_grid, kde_np, color="#64748b", alpha=0.12)

# Hierarchical Density (Emerald / Solid)
ax2.plot(x_grid, kde_hier, color="#059669", lw=2.6,
         label=f"Hierarchical Bayes (Option C)\nMedian: +{np.median(hier_lead):.1f}% [{np.percentile(hier_lead, 2.5):.1f}%, {np.percentile(hier_lead, 97.5):.1f}%]")
ax2.fill_between(x_grid, kde_hier, color="#059669", alpha=0.22)

# Vertical Reference Lines
ax2.axvline(0, color="#e11d48", linestyle=":", lw=1.5, label="Tie Margin (0%)")
ax2.axvline(np.median(hier_lead), color="#059669", linestyle="-", lw=1.8)
ax2.axvline(np.median(nopool_lead), color="#64748b", linestyle="--", lw=1.5)

# Annotation for increase in lead
ax2.annotate(
    f"National Bush Lead climbs\nfrom +{np.median(nopool_lead):.1f}% to +{np.median(hier_lead):.1f}%\n(Dukakis fluke strata 1 & 5 shrunken in)",
    xy=(np.median(hier_lead), kde_hier.max() * 0.72),
    xytext=(np.median(hier_lead) + 2.4, kde_hier.max() * 0.80),
    arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5),
    fontsize=9, fontweight="bold", color="#065f46",
    bbox=dict(boxstyle="round,pad=0.4", fc="#ecfdf5", ec="#059669", lw=1.2)
)

ax2.set_xlabel("Bush Lead Margin Among Decided Voters (%)", fontsize=11, fontweight="bold", labelpad=8)
ax2.set_ylabel("Posterior Probability Density", fontsize=11, fontweight="bold", labelpad=8)
ax2.set_title("B. Poststratified National Election Margin\n$\\Delta = 2 \\alpha_{1,\\text{national}} - 1$ (Bush $-$ Dukakis)",
              fontsize=12, fontweight="bold", pad=12, loc="left")
ax2.set_xlim(-2, 22)
ax2.legend(loc="upper right", fontsize=8.5, frameon=True, facecolor="white", framealpha=0.95)
ax2.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
fig.savefig("bda3/ch8/figures/ch8_stratified_shrinkage.png", dpi=300, bbox_inches="tight")
fig.savefig("bda3/ch8/figures/ch8_stratified_shrinkage.svg", bbox_inches="tight")
print("Figure 8.4 generated successfully as SVG and PNG.")
