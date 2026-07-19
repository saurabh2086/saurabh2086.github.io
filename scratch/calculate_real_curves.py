import math

# --- 8 Schools Data ---
y_8 = [28.4, 7.9, -3.0, 6.8, -0.6, 1.4, 18.0, 12.2]
sigma_8 = [14.9, 10.2, 16.3, 11.0, 8.5, 11.4, 10.4, 17.6]

# --- 3 Schools Data ---
y_3 = [28.4, 7.9, -3.0]
sigma_3 = [14.9, 10.2, 16.3]

def calc_log_marginal_likelihood(t, y, sigma):
    # If tau is extremely close to 0, prevent division by zero or log(0)
    t = max(t, 1e-4)
    precisions = [1.0 / (s**2 + t**2) for s in sigma]
    V_mu = 1.0 / sum(precisions)
    mu_hat = sum(yj * p for yj, p in zip(y, precisions)) * V_mu
    
    term1 = 0.5 * math.log(V_mu)
    term2 = -0.5 * sum(math.log(s**2 + t**2) for s in sigma)
    term3 = -0.5 * sum(((yj - mu_hat)**2) / (s**2 + t**2) for yj, s in zip(y, sigma))
    
    return term1 + term2 + term3

# ==========================================
# 1. Figure 5.9 (J=8), tau from 0 to 40.
# Grid size: 100 steps
# ==========================================
tau_grid_8 = [i * 0.4 for i in range(101)] # 0 to 40

# (a) Uniform Prior on tau: p(tau) \propto 1
# Log posterior = log marginal likelihood
log_post_uni = [calc_log_marginal_likelihood(t, y_8, sigma_8) for t in tau_grid_8]
max_log_uni = max(log_post_uni)
post_uni = [math.exp(lp - max_log_uni) for lp in log_post_uni]

# (b) Inverse-Gamma(1, 1) on tau^2: p(tau) \propto tau^-3 * exp(-1/tau^2)
def log_prior_ig11(t):
    if t < 0.1: # prevent log(0) and division by zero
        return -999.0
    return -3.0 * math.log(t) - 1.0 / (t**2)

log_post_ig11 = []
for t in tau_grid_8:
    lm = calc_log_marginal_likelihood(t, y_8, sigma_8)
    lp = log_prior_ig11(t)
    log_post_ig11.append(lm + lp)

max_log_ig11 = max(log_post_ig11)
post_ig11 = [math.exp(lp - max_log_ig11) for lp in log_post_ig11]

# Prior curve for IG(1, 1) scaled to look nice
prior_ig11_vals = [math.exp(log_prior_ig11(t)) for t in tau_grid_8]
max_prior_ig11 = max(prior_ig11_vals)
prior_ig11_scaled = [p / max_prior_ig11 for p in prior_ig11_vals]

# (c) Inverse-Gamma(0.001, 0.001) on tau^2: p(tau) \propto tau^-1.002 * exp(-0.001/tau^2)
def log_prior_ig001(t):
    if t < 0.01:
        return 10.0 # large spike near zero
    return -1.002 * math.log(t) - 0.001 / (t**2)

log_post_ig001 = []
for t in tau_grid_8:
    lm = calc_log_marginal_likelihood(t, y_8, sigma_8)
    lp = log_prior_ig001(t)
    log_post_ig001.append(lm + lp)

max_log_ig001 = max(log_post_ig001)
post_ig001 = [math.exp(lp - max_log_ig001) for lp in log_post_ig001]

# Prior curve for IG(0.001, 0.001) scaled
prior_ig001_vals = [math.exp(log_prior_ig001(t)) if t > 0 else 0 for t in tau_grid_8]
max_prior_ig001 = max(prior_ig001_vals)
prior_ig001_scaled = [p / max_prior_ig001 if max_prior_ig001 > 0 else 0 for p in prior_ig001_vals]

# ==========================================
# 2. Figure 5.10 (J=3), tau from 0 to 150.
# Grid size: 100 steps
# ==========================================
tau_grid_3 = [i * 1.5 for i in range(101)] # 0 to 150

# (a) Uniform prior on tau: log post = log marginal likelihood
log_post_uni_3 = [calc_log_marginal_likelihood(t, y_3, sigma_3) for t in tau_grid_3]
max_log_uni_3 = max(log_post_uni_3)
post_uni_3 = [math.exp(lp - max_log_uni_3) for lp in log_post_uni_3]

# (b) Half-Cauchy(25) prior on tau: p(tau) \propto 1 / (1 + (tau/25)^2)
def log_prior_cauchy25(t):
    return -math.log(1.0 + (t / 25.0)**2)

log_post_cauchy_3 = []
for t in tau_grid_3:
    lm = calc_log_marginal_likelihood(t, y_3, sigma_3)
    lp = log_prior_cauchy25(t)
    log_post_cauchy_3.append(lm + lp)

max_log_cauchy_3 = max(log_post_cauchy_3)
post_cauchy_3 = [math.exp(lp - max_log_cauchy_3) for lp in log_post_cauchy_3]

# Prior curve for Cauchy(25) scaled
prior_cauchy_vals = [math.exp(log_prior_cauchy25(t)) for t in tau_grid_3]
# We want to scale the prior curve relative to the posterior peak to look good visually
prior_cauchy_scaled = [p for p in prior_cauchy_vals] # Cauchy prior starts at 1 at tau=0

# ==========================================
# Helper to print SVG paths
# ==========================================
def print_path(x_start, x_scale, y_baseline, y_height, grid, values):
    points = []
    for t, v in zip(grid, values):
        x = x_start + x_scale * t
        y = y_baseline - y_height * v
        points.append(f"{x:.1f},{y:.1f}")
    return "M " + " L ".join(points)

print("=== FIGURE 5.9 (8 schools, tau 0 to 40, x_scale=10) ===")
print("Uniform Posterior path (d attribute):")
path_uni = print_path(50, 10.0, 210, 170, tau_grid_8, post_uni)
# Close path for filled area: starts at x=50,y=210, goes to path, then down to x_last,y=210, then back to start
print(f"{path_uni} L 450,210 L 50,210 Z")

print("\nIG(1,1) Posterior path:")
path_ig11 = print_path(50, 10.0, 210, 170, tau_grid_8, post_ig11)
print(f"{path_ig11} L 450,210 L 50,210 Z")

print("\nIG(1,1) Prior path (no close):")
print(print_path(50, 10.0, 210, 150, tau_grid_8, prior_ig11_scaled))

print("\nIG(0.001,0.001) Posterior path:")
path_ig001 = print_path(50, 10.0, 210, 170, tau_grid_8, post_ig001)
print(f"{path_ig001} L 450,210 L 50,210 Z")

print("\nIG(0.001,0.001) Prior path (no close):")
print(print_path(50, 10.0, 210, 150, tau_grid_8, prior_ig001_scaled))

print("\n=== FIGURE 5.10 (3 schools, tau 0 to 150, x_scale=1.2) ===")
print("Uniform(0, inf) Posterior path:")
# Note: For Figure 5.10, x goes from 30 to 210 (width 180, so x_scale = 1.2)
# y baseline is 160, peak height is 130
path_uni_3 = print_path(30, 1.2, 160, 130, tau_grid_3, post_uni_3)
print(f"{path_uni_3} L 210,160 L 30,160 Z")

print("\nHalf-Cauchy(25) Posterior path:")
path_cauchy_3 = print_path(30, 1.2, 160, 130, tau_grid_3, post_cauchy_3)
print(f"{path_cauchy_3} L 210,160 L 30,160 Z")

print("\nHalf-Cauchy(25) Prior path (no close):")
# Scale the Cauchy prior so it starts at y = 160 - 80 = 80 at tau = 0
print(print_path(30, 1.2, 160, 80, tau_grid_3, prior_cauchy_scaled))
