# Prior TrueSkill Runs

## Run 1: Telegram Channel Prune (Feb 2026)

Mode: Pairwise
Items: 42 Telegram channels
Matchups: 504 (12x coverage per channel)
Batches: 21 (25 matchups each)
Engine: Codex Spark (gpt-5.4-codex-spark)
Parse error rate: <2%

Results:
- GOLD tier (top 35%): 15 channels
- KEEP tier (middle): 17 channels
- PRUNE tier (bottom 25%): 10 channels
- Top channel win rate: 90%
- Bottom channel win rate: 4%
- Min appearances per channel: 15
- Mean appearances per channel: 24

Rubric: practitioner-signal (6 criteria)

## Run 2: Telegram Channel Discovery (Feb 2026)

Mode: Pairwise
Items: 28 candidate channels vs 10 GOLD anchors
Matchups: ~336 (12+ per candidate)
Engine: Codex Spark
Subscribe threshold: conservative >= 18.0

Results:
- SUBSCRIBE: 14 channels
- REJECT: 14 channels
- Top candidate conservative score: 23.74
- Bottom rejected score: -0.39

Rubric: practitioner-signal (6 criteria)

## Lessons Learned

1. Codex Spark at reasoning=low produces reliable JSON for ranking tasks
2. Parse error rate consistently <5% with layered JSON extraction
3. draw_probability=0.0 works well for batch mode; 0.05 for pairwise
4. Overlap of 3-4 provides stable rankings; overlap 2 is too noisy
5. Inverse-frequency weighted sampling produces even coverage (min appearances within 1 of target)
6. Rubric ordering matters -- placing PRACTITIONER SIGNAL first consistently produces the desired quality signal
7. Post text cap of 1500 chars is sufficient; longer text causes Spark to truncate or hallucinate
8. The conservative score (mu - 3*sigma) correctly penalizes items with few appearances
