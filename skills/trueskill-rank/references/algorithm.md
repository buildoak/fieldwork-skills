# TrueSkill Algorithm Reference

## Core Concept
TrueSkill models each item as a Gaussian N(mu, sigma^2). mu = estimated quality, sigma = uncertainty. Originally designed by Microsoft for Xbox Live multiplayer matchmaking.

## Two Update Modes

### 1v1 (Pairwise)
- rate_1vs1(winner, loser)
- Winner mu increases, loser decreases
- Both sigmas decrease (more data = less uncertainty)
- Magnitude depends on how surprising the outcome was (upset = larger update)
- Python: winner_new, loser_new = env.rate_1vs1(winner_rating, loser_rating)

### N-Player Free-for-all (Batch)
- rate(teams) where each team is [rating] (1-player team)
- Teams ordered by placement (1st, 2nd, ... Nth)
- Uses factor graph belief propagation across all N players
- Higher-placed items get mu increases; lower get decreases
- Correctly handles transitivity: if A > B > C, infers A >> C
- One call to rate() is statistically more efficient than N*(N-1)/2 individual rate_1vs1 calls because TrueSkill exploits the transitive structure
- Python: new_teams = env.rate(teams)  # teams = [[r1], [r2], ..., [rN]] ordered best-to-worst

## Key Parameters

| Parameter | Typical Value | Meaning |
|-----------|--------------|---------|
| mu (initial) | 25.0 | Starting quality estimate |
| sigma (initial) | 8.333 (25/3) | Starting uncertainty |
| draw_probability | 0.0 (batch) or 0.05 (pairwise) | Probability of a draw |
| beta | sigma/2 = 4.167 | Performance variance |
| tau | sigma/100 = 0.083 | Dynamics factor (prevents sigma from going to 0) |

## Conservative Score

conservative = mu - 3 * sigma

This is the lower bound of the 99.7% confidence interval. It penalizes uncertainty -- an item with mu=30, sigma=5 (conservative=15) ranks below an item with mu=27, sigma=2 (conservative=21). More appearances = lower sigma = more trust in the rating.

## Convergence

With N items and overlap K (each item appears in K subsets):
- K=2: rough ordering, sigma remains high
- K=3: good convergence, rankings stable
- K=4: strong convergence, sigma low enough for tier boundaries

Minimum viable: each item should appear in at least 2 subsets. Below this, sigma dominates and rankings are meaningless.

## Subset Generation: Inverse-Frequency Weighted Sampling

To ensure even coverage, use inverse-frequency weighted sampling:
- Weight for each item = 1 / (1 + appearance_count)
- Items with fewer appearances get selected more often
- This naturally converges to uniform coverage

Number of subsets = ceil(N * overlap / subset_size)

For 100 items, overlap=3, subset_size=10: 30 subsets, each item in ~3 subsets.

## Implicit Comparisons

Each batch ranking of K items produces C(K,2) = K*(K-1)/2 implicit pairwise comparisons.

| Subset size | Implicit comparisons per subset |
|-------------|-------------------------------|
| 5 | 10 |
| 8 | 28 |
| 10 | 45 |
| 15 | 105 |

For 30 subsets of 10: 30 * 45 = 1,350 implicit comparisons from just 30 API calls.

## Cost Scaling

| Items | Overlap | Subsets | API calls | Implicit comparisons |
|-------|---------|---------|-----------|---------------------|
| 50 | 3 | 15 | 15 | 675 |
| 100 | 3 | 30 | 30 | 1350 |
| 200 | 3 | 60 | 60 | 2700 |
| 500 | 3 | 150 | 150 | 6750 |
| 100 | 4 | 40 | 40 | 1800 |

## Python Library
pip install trueskill
Version 0.4.5. Pure Python. No C extensions needed.
