# fatiguelab

MSD risk assessment tools based on fatigue failure theory, implementing three models developed by Gallagher, Sesek, Schall et al. at Auburn University:

- **LiFFT** — Lifting Fatigue Failure Tool (low back disorder risk)
- **DUET** — Distal Upper Extremity Tool (hand/wrist/forearm disorder risk)
- **Shoulder Tool** — shoulder disorder risk

All three models apply the same principle: cumulative micro-damage from repeated loading predicts injury risk, just like metal fatigue predicts structural failure. They use S-N curves and the Palmgren-Miner cumulative damage rule adapted to biological tissues.

## Install

```bash
uv tool install fatiguelab          # from PyPI
uv tool install -e .                # editable, from source
```

## CLI

The command-line tool is `fl`:

```bash
# List available models
fl --list

# LiFFT: 15kg load, 0.45m from spine, 600 reps
fl lifft -t 15,0.45,600

# Multi-task assessment
fl lifft -t 15,0.45,600,Palletizing -t 5,0.3,300,Light_picks -t 25,0.55,80,Heavy_bags

# DUET: OMNI effort 4, 1350 reps
fl duet -t 4,1350

# Shoulder: 3lb load, 20in reach, 1500 reps
fl shoulder -t 3,20,1500,Stocking
fl shoulder --task-type push_pull -t 10,12,200,Cart_pushing
```

## Web app

```bash
uv run uvicorn fatiguelab.api:app
```

Open http://127.0.0.1:8000 for an interactive UI with scenario comparison.

## Python API

```python
from fatiguelab.models import LiFFT, Task

model = LiFFT()
tasks = [
    Task(name="Palletizing", params={"load_kg": 15, "distance_m": 0.45, "reps": 600}),
    Task(name="Light picks", params={"load_kg": 5, "distance_m": 0.3, "reps": 300}),
]
result = model.assess(tasks)
print(f"Cumulative damage: {result.cumulative_damage:.6f}")
print(f"Probability: {result.probability:.1%}")
```

## Development

```bash
uv sync                             # install dependencies
uv run pytest                       # run tests (95 tests)
uv run --with ruff ruff check src/  # lint
uv run --with ty ty check src/      # type check
```

## References

- Gallagher et al. (2017) "Development and validation of an easy-to-use risk assessment tool for cumulative low back loading: The Lifting Fatigue Failure Tool (LiFFT)." *Applied Ergonomics*, 63, 142-150.
- Gallagher et al. (2018) "An Upper Extremity Risk Assessment Tool Based on Material Fatigue Failure Theory: The Distal Upper Extremity Tool (DUET)." *Human Factors*, 60(8), 1146-1162.
- Bani Hani et al. (2021) "Development and validation of a cumulative exposure shoulder risk assessment tool based on fatigue failure theory." *Ergonomics*, 64(1), 39-54.

See [docs/research.md](docs/research.md) for detailed notes on the theoretical foundation, formulas, and confidence assessments.

## Origin

This project was originally developed during an agentic coding demo for Auburn's INSY 7740 course, demonstrating the progression from research extraction through specification-driven development to a working tool. The original demo state is preserved at the [`demo-rehearsal`](../../tree/demo-rehearsal) tag.
