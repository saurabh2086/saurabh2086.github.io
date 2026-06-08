import random
import math

def run_simulation():
    # Parameters
    N = 100               # Number of developers
    K = 10.0              # Total resource budget
    T_0 = 1.0             # Baseline completion time
    theta = 0.1           # Time cost of rigor (significant but not overwhelming)
    gamma = 0.5           # Temporal discount sensitivity
    alpha = 0.0           # Cost coefficient of presentation (free presentation under GenAI)
    beta = 0.3            # Cost coefficient of rigor
    w_u = 10.0            # Weight of organizational approval
    w_r_mean = 1.5        # Mean of intrinsic technical pride
    w_r_std = 0.5         # Std of intrinsic technical pride
    w_hat_r = 2.0         # Evaluator's weight of perceived rigor
    w_hat_p = 1.0         # Evaluator's weight of perceived presentation
    beta_halo = 0.4       # Evaluator's halo effect coefficient
    
    # Initialize developer populations
    random.seed(42)
    w_r = [max(0.1, random.normalvariate(w_r_mean, w_r_std)) for _ in range(N)]
    
    # Strategies (K_R effort allocated to rigor)
    # Start with some random positive rigor
    K_R = [random.uniform(2.0, 5.0) for _ in range(N)]
    
    def simulate_regime(w_L, lambda_audit, use_reject_option=False, rounds=50):
        K_R_curr = list(K_R)
        
        for r in range(rounds):
            # Calculate completion times
            T = [T_0 + theta * kr for kr in K_R_curr]
            
            # Peer benchmark (mean completion time of others)
            T_bench = []
            for i in range(N):
                others_T = T[:i] + T[i+1:]
                T_bench.append(sum(others_T) / len(others_T))
                
            # Update strategies
            K_R_next = list(K_R_curr)
            for i in range(N):
                best_kr = 0.0
                best_util = -float('inf')
                
                # 200 grid candidates in [0, K]
                for step in range(201):
                    k_r_val = (step / 200.0) * K
                    k_p_val = K - k_r_val
                    t_val = T_0 + theta * k_r_val
                    d_val = math.exp(-gamma * max(0.0, t_val - T_bench[i]))
                    
                    # Evaluator observations
                    s_r = k_r_val
                    s_p = k_p_val
                    
                    # Perceived rigor under unified Bayesian posterior
                    r_hat = lambda_audit * s_r + (1 - lambda_audit) * beta_halo * s_p
                    p_hat = s_p
                    u_hat = w_hat_r * r_hat + w_hat_p * p_hat
                    
                    # Ruin probability contribution
                    if use_reject_option:
                        p_ruin = 0.05 / (1.0 + k_r_val) # reject option caps ruin probability
                    else:
                        p_ruin = 15.0 / (1.0 + k_r_val) # high tail risk penalty for low rigor
                        
                    u_dev = w_u * u_hat * d_val + w_r[i] * k_r_val - beta * (k_r_val**2) - alpha * (k_p_val**2) - w_L * p_ruin
                    
                    if u_dev > best_util:
                        best_util = u_dev
                        best_kr = k_r_val
                        
                K_R_next[i] = best_kr
                
            # Smooth update
            K_R_curr = [0.8 * curr + 0.2 * nxt for curr, nxt in zip(K_R_curr, K_R_next)]
            
        return K_R_curr

    print("--- Running Toy Numerical Simulation ---")
    
    # Regime 1: High Time Pressure, Low Liability (w_L = 0.0), Visually Biased Audit (lambda = 0.1)
    KR_regime1 = simulate_regime(w_L=0.0, lambda_audit=0.1, rounds=100)
    mean_kr_1 = sum(KR_regime1) / len(KR_regime1)
    attracted_1 = sum(1 for kr in KR_regime1 if kr < 1.0)
    stressed_1 = sum(1 for kr in KR_regime1 if kr >= 1.0)
    print(f"Regime 1 (Spectacle): Mean Rigor K_R = {mean_kr_1:.2f} (Budget: {K})")
    print(f"  Attracted Cluster (Rigor < 1.0): {attracted_1}% of developers")
    print(f"  Stressed Minority (Rigor >= 1.0): {stressed_1}% of developers")
    
    # Regime 2: Epistemic Restoration (w_L = 15.0, Blinded Audit lambda = 1.0, Reject Option enabled)
    KR_regime2 = simulate_regime(w_L=15.0, lambda_audit=1.0, use_reject_option=True, rounds=100)
    mean_kr_2 = sum(KR_regime2) / len(KR_regime2)
    restored_2 = sum(1 for kr in KR_regime2 if kr >= 4.0)
    print(f"\nRegime 2 (Epistemic Restoration): Mean Rigor K_R = {mean_kr_2:.2f}")
    print(f"  Rigor Restored (Rigor >= 4.0): {restored_2}% of developers")

if __name__ == "__main__":
    run_simulation()
