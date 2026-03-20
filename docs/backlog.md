# Backlog

## Low effort, high value

- CSV/JSON import/export for task sets - save and reload assessments, share between colleagues
- `fl compare` - CLI equivalent of the web app's baseline comparison (before/after scenarios in one command)
- Print-friendly report output from the web app (an ergonomist needs to hand something to a plant manager)

## Medium effort, builds on what's here

- Anthropometry profiles - sex, percentile, or custom body dimensions. Right now Shoulder Tool hardcodes 50th percentile male (681 in-lb, 8.6 lb arm weight). LiFFT's spine strength could also vary by age/sex. Let the user select a profile and the model adjusts its strength reference values.
- Pose-aware LiFFT - instead of requiring the user to measure horizontal distance, let them specify posture (standing upright, bent forward, arms extended) and load position (floor, knuckle, shoulder height). Derive the moment arm from anthropometric models. This is basically what 3DSSPP does, but simplified.
- Batch mode - `fl batch scenarios.csv` processes a whole shift's worth of tasks from a file and generates a report

## Bigger scope, real differentiation

- Shift timeline - tasks aren't uniform across a day. Model task sequences with durations and rest periods. The framework supports this (Palmgren-Miner is additive) but the current tools flatten everything to daily totals.
- Multi-body-region dashboard - run all three models on the same job and show a whole-body risk profile. A warehouse job has back risk *and* shoulder risk *and* hand/wrist risk.
- Healing/recovery factor - the research notes mention ~1% tendon recovery per day. No existing tool models this, but multi-day cumulative exposure with recovery would be novel.
