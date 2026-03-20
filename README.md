# fatiguelab

MSD risk assessment tools based on fatigue failure theory, implementing three models developed by Gallagher, Sesek, Schall et al. at Auburn University:

- *LiFFT* - Lifting Fatigue Failure Tool (low back disorder risk)
- *DUET* - Distal Upper Extremity Tool (hand/wrist/forearm disorder risk)
- *Shoulder Tool* - shoulder disorder risk

All three models apply the same principle: cumulative micro-damage from repeated loading predicts injury risk, just like metal fatigue predicts structural failure. They use S-N curves and the Palmgren-Miner cumulative damage rule adapted to biological tissues.

For detailed notes on the theoretical foundation, formulas, data sources, and confidence assessments, see [docs/research.md](docs/research.md).

## Try it

Install with a single command (installs [uv](https://docs.astral.sh/uv/) automatically if needed):

```bash
curl -LsSf uvx.sh/fatiguelab/install.sh | sh
```

Then run the interactive demo:

```bash
fl demo
```

Or start the web app at http://127.0.0.1:8000:

```bash
fl serve
```

## Install for command-line use

If you already have [uv](https://docs.astral.sh/uv/getting-started/installation/), you can run fatiguelab without installing:

```bash
uvx fatiguelab demo
uvx fatiguelab lifft -t 10,0.4,500
```

Or install it as a permanent tool (makes the `fl` shorthand available):

```bash
uv tool install fatiguelab
```

## CLI

Once installed, the command-line tool is `fl`:

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

# Interactive demo
fl demo

# Web app
fl serve
```

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
git clone https://github.com/YOUR_ORG/fatiguelab.git
cd fatiguelab
uv sync                             # install dependencies
uv tool install -e .                # editable install (fl reflects source changes)
uv run pytest                       # run tests (95 tests)
uv run --with ruff ruff check src/  # lint
uv run --with ty ty check src/      # type check
```

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Origin

This project was originally developed during an agentic coding demo for Auburn's INSY 7740 course, demonstrating the progression from research extraction through specification-driven development to a working tool. The original demo state is preserved at the [`demo-rehearsal`](../../tree/demo-rehearsal) tag.
