# Project Rules and Guidelines

## 1. Designing Interactive Probability Agents and Simulations

When designing or implementing interactive game-theoretic or probabilistic agents (like bandits, RPS agents, or statistical simulators) in this workspace:
- **UI-Aligned Monte Carlo Estimation**: If the user interface displays the agent's probability distribution or decision cloud (e.g. strategy progress bars), do not simply run a single Thompson sampling draw and return its argmax. Instead, run the draw-and-argmax step multiple times (e.g., 2000 parallel trials) to estimate the action distribution, then sample the final move from it. This keeps the UI rendering smooth and informative while remaining mathematically equivalent to a single draw.
- **Ensemble Blending**: Prefer integrating out expert/model uncertainty (e.g., averaging posterior draws weighted by trust weights) rather than selecting a single expert's prediction.
- **Behavioral Coordinate Mapping**: In small-sample online learning, look for coordinate transformations that compress the state space. For example, map absolute moves to outcome-relative transitions (like Win-Stay/Lose-Shift repeat/shift actions) to accelerate convergence.

## 2. Authoring Technical Social Media Posts (LinkedIn)

When drafting LinkedIn or other social media posts about workspace projects:
- **Humble & Reflective Tone**: Start with a personal belief or reflection (e.g., the value of building algorithms from scratch to learn). Focus on personal discovery and return-to-basics rather than boastful claims or criticizing out-of-the-box libraries.
- **Conceptual Explanation over Jargon**: Explain the intuition behind custom algorithms (e.g., starting with flat baseline counts to represent ignorance and scaling confidence as data accumulates) conceptually. Avoid using formal academic names of distributions (like "Dirichlet") unless explicitly requested.
