"""
semiotic_decay_pooling_sim.py
--------------------------------
Agent-based simulation of the developer pooling game from
"The Semiotic Decay of AI Analytics" (Section 6.6).

The decisive mechanism is a *validation gate* (the blinded audit of 6.2):
a project deploys only if perceived rigor

    R_hat = lambda_audit * K_R + (1 - lambda_audit) * B_halo * S_P

clears a threshold V_thresh, where S_P = K - K_R (the binding budget
constraint: every hour of rigor is an hour taken from presentation).

Each of N developers picks K_R in [0, K] by noisy best response to the
mean-field peer timeline benchmark, to convergence. Presentation is
commoditised (alpha = 0); rigor cost is convex (beta); a temporal-discount
penalty exp(-gamma * overrun) punishes overrunning the peer benchmark;
limited liability enters as w_{L,i} * exp(-kappa * K_R) with
w_{L,i} = min(w_L, wealth_i) against a log-normal wealth distribution
(the 6.1 limited-liability ceiling).

Reproducible: fixed seeds 0..19, results reported as means over seeds.
"""

import numpy as np

# ----------------------------- parameters -----------------------------
N            = 100      # developers
K            = 10.0     # per-developer budget (K_R + K_P = K)
ALPHA        = 0.0      # presentation marginal cost (commoditised)
BETA         = 0.3      # convex rigor cost coefficient
THETA        = 0.1      # time multiplier of rigor (T = T0 + theta*K_R)
GAMMA        = 0.5      # organizational impatience coefficient
T0           = 1.0      # wrapper baseline timeline
B_HALO       = 1.0      # presentation->rigor halo cross-loading
V_THRESH     = 4.0      # validation gate threshold
W_U          = 10.0     # weight on perceived utility (deploy benefit)
W_RHAT       = 1.0      # cognitive weight on perceived rigor
W_PHAT       = 1.0      # cognitive weight on perceived presentation
KAPPA        = 0.5      # liability decay rate in K_R
WEALTH_MU    = 0.0      # log-normal wealth: mean of underlying normal
WEALTH_SIG   = 1.0      # log-normal wealth: sd of underlying normal
GRID         = np.linspace(0.0, K, 501)   # K_R candidate grid
N_ITERS      = 200      # mean-field best-response iterations
DAMPING      = 0.5      # update damping for stability
CHOICE_NOISE = 0.02     # sd of multiplicative noise on chosen K_R
SEEDS        = range(20)


def developer_utility(K_R, peer_mean_KR, lam, wealth_cap):
    """Vectorised utility: K_R is grid (G,), wealth_cap is (N,). Returns (N,G)."""
    S_P   = K - K_R                                  # (G,)
    R_hat = lam * K_R + (1.0 - lam) * B_HALO * S_P   # (G,)
    deploys = (R_hat >= V_THRESH).astype(float)      # (G,)

    T_i      = T0 + THETA * K_R
    T_bench  = T0 + THETA * peer_mean_KR
    overrun  = np.maximum(0.0, T_i - T_bench)
    discount = np.exp(-GAMMA * overrun)

    U_perceived = W_RHAT * R_hat + W_PHAT * S_P
    benefit     = W_U * U_perceived * discount * deploys      # (G,)
    cost        = BETA * K_R ** 2 + ALPHA * S_P               # (G,)
    base        = (benefit - cost)[None, :]                   # (1,G)
    liability   = wealth_cap[:, None] * np.exp(-KAPPA * K_R)[None, :]  # (N,G)
    return base - liability                                   # (N,G)


def run(lam, w_L, seed):
    rng = np.random.default_rng(seed)
    wealth     = rng.lognormal(WEALTH_MU, WEALTH_SIG, size=N)
    wealth_cap = np.minimum(w_L, wealth)        # 6.1 limited-liability ceiling
    K_R        = np.zeros(N)                     # start at the pooling corner

    for _ in range(N_ITERS):
        peer_mean = K_R.mean()
        u = developer_utility(GRID, peer_mean, lam, wealth_cap)   # (N,G)
        best = GRID[np.argmax(u, axis=1)]                         # (N,)
        best = best * (1.0 + CHOICE_NOISE * rng.standard_normal(N))
        new_KR = np.clip(best, 0.0, K)
        K_R = DAMPING * K_R + (1.0 - DAMPING) * new_KR
    return K_R



def mean_over_seeds(lam, w_L):
    finals = [run(lam, w_L, s) for s in SEEDS]
    pop = np.concatenate(finals)
    return pop.mean(), pop.std()


if __name__ == "__main__":
    print("=== Two headline regimes ===")
    m1, s1 = mean_over_seeds(lam=0.1, w_L=0.0)
    print(f"Regime 1 (Spectacle:  lambda=0.1, w_L=0 ):  K_R = {m1:.2f}  (sd {s1:.2f})")
    m2, s2 = mean_over_seeds(lam=0.9, w_L=15.0)
    print(f"Regime 2 (Restoration:lambda=0.9, w_L=15):  K_R = {m2:.2f}  (sd {s2:.2f})")

    print("\n=== Phase boundary: sweep lambda at w_L=0 ===")
    for lam in [0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 0.90, 0.95]:
        m, _ = mean_over_seeds(lam=lam, w_L=0.0)
        print(f"  lambda={lam:.2f}  ->  mean K_R = {m:.2f}")

    print("\n=== Ablation (lambda, w_L) ===")
    for lam, wL, tag in [(0.9, 0.0, "audit gate only"),
                         (0.1, 15.0, "liability only"),
                         (0.9, 15.0, "both")]:
        m, _ = mean_over_seeds(lam=lam, w_L=wL)
        print(f"  {tag:16s} (lambda={lam}, w_L={wL}):  K_R = {m:.2f}")

    print("\n=== Analytic gate check ===")
    lam_star = 1.0 - V_THRESH / (B_HALO * K)
    print(f"  corner K_R=0 clears gate iff lambda <= {lam_star:.2f}")
