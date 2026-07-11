import math

# Data from Table 5.2
y = [28.4, 7.9, -3.0, 6.8, -0.6, 1.4, 18.0, 12.2]
sigma = [14.9, 10.2, 16.3, 11.0, 8.5, 11.4, 10.4, 17.6]

# Grid for tau (0 to 25 with 100 steps)
tau_grid = [i * 0.25 for i in range(101)]

def calculate_log_p_tau(t):
    # Calculate V_mu and mu_hat for given tau
    precisions = [1.0 / (s**2 + t**2) for s in sigma]
    V_mu = 1.0 / sum(precisions)
    mu_hat = sum(yj * p for yj, p in zip(y, precisions)) * V_mu
    
    # Calculate log marginal likelihood
    term1 = 0.5 * math.log(V_mu)
    term2 = -0.5 * sum(math.log(s**2 + t**2) for s in sigma)
    term3 = -0.5 * sum(((yj - mu_hat)**2) / (s**2 + t**2) for yj, s in zip(y, sigma))
    
    return term1 + term2 + term3

# Evaluate log_p on grid
log_p_vals = [calculate_log_p_tau(t) for t in tau_grid]

# Find max for numerical stability and normalization
max_log_p = max(log_p_vals)
p_vals = [math.exp(lp - max_log_p) for lp in log_p_vals]

# Map to SVG:
# tau goes from 0 to 25 -> x goes from 50 to 450 (width 400, so x = 50 + 16 * tau)
# p_val goes from 0 to 1 -> y goes from 180 (p=0) to 30 (p=1) (height 150, so y = 180 - 150 * p_val)

path_points = []
for t, p in zip(tau_grid, p_vals):
    x = 50 + 16 * t
    y_coord = 180 - 150 * p
    path_points.append(f"{x:.1f},{y_coord:.1f}")

path_str = "M " + " L ".join(path_points)
print("--- Figure 5.5 (p(tau | y)) Path ---")
print(path_str)
