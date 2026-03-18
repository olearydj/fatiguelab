# Fatigue Failure Risk Calculator - Web App

## Problem Statement

Ergonomists and safety professionals need to assess musculoskeletal disorder risk from repetitive work tasks. Three validated models exist (LiFFT, DUET, Shoulder Tool) but the current web implementations only evaluate one scenario at a time. Comparing "before and after" an intervention requires running the tool twice and doing the comparison manually. This makes it hard to use the tools as decision-making instruments when proposing workplace changes to managers.

## Domain Research

See `RESEARCH.md` for the full domain research, including the mathematical models, validation data, and published test cases. The calculation engine in `fatigue_calc.py` implements all three models and has 76 passing tests, including verification against published examples.

## Constitution

These values guide design decisions when tradeoffs arise.

- Accuracy first - the math must match the published models exactly; a tool that looks good but computes wrong is worthless
- Transparency - show users how the number was calculated, not just the result; an ergonomist needs to defend their recommendation to stakeholders
- Accessibility - a plant manager with no ergonomics background should understand the output; an ergonomist shouldn't need a manual to use the tool
- Comparison is the point - the tool's unique value is answering "what if"; every design decision should make before/after comparison effortless
- Build on what works - the CLI calculator is tested and correct; the web app wraps it, never reimplements it

## Specification

### What the app does

The app lets users assess musculoskeletal disorder risk for a set of work tasks and compare scenarios to evaluate interventions.

### Core workflow

1. User selects a body region (low back, hand/wrist, shoulder) and the appropriate model loads
2. User builds a task list describing the workday - each task has the inputs that model requires
3. Results appear immediately as the task list changes - no submit button, no waiting
4. User can snapshot the current scenario as a baseline, modify tasks, and see how the changes affect risk side by side

### What the user sees

Results include:

- Cumulative damage (numeric value)
- Probability of injury outcome (percentage)
- Each task's contribution to total damage (percentage and visual proportion)
- Risk level communicated through color: green (< 25%), yellow (25-50%), red (> 50%)

When comparing scenarios:

- Both scenarios displayed side by side
- Change in cumulative damage shown as absolute and percentage
- Change in probability shown as absolute difference
- Delta color-coded: green if risk decreased, red if increased

### Model-specific inputs

LiFFT (low back):

- Load weight (kg)
- Horizontal distance from spine to load (m)
- Repetitions per workday

DUET (hand/wrist/forearm):

- OMNI-RES effort rating (0-10 scale with descriptors)
- Repetitions per workday

Shoulder Tool:

- Load or force (lb)
- Distance from acromion to load (in)
- Repetitions per workday
- Task type (handling, push/pull, push down)

### Why scenario comparison matters

The existing Auburn tools evaluate one scenario at a time. An ergonomist has to run the tool twice, write down numbers, and compare mentally. Making this instant and visual turns the tool from an assessment instrument into a decision-making instrument. It lets an ergonomist sit with a plant manager and say: "here's the current risk, and here's what happens if we add a lift assist" - with the answer appearing immediately.

## Plan

### Architecture

```text
┌─────────────────────────────┐
│  Browser (single page)      │
│  HTML + CSS + vanilla JS    │
└──────────┬──────────────────┘
           │ fetch() / JSON
┌──────────▼──────────────────┐
│  FastAPI server              │
│  Thin wrapper over calc core │
└──────────┬──────────────────┘
           │ Python imports
┌──────────▼──────────────────┐
│  fatigue_calc.py             │
│  (existing, tested)          │
└─────────────────────────────┘
```

### Technology choices

- Python / FastAPI for the backend - lightweight, serves both API and static files
- Vanilla HTML / CSS / JS for the frontend - no build step, no framework, no npm
- All calculation logic stays in `fatigue_calc.py` - the API never reimplements math
- Single command startup: `python app.py`

### API design

Two endpoints, both JSON.

`GET /api/models` - returns available models with their input field definitions (name, label, type, constraints). The frontend uses this to dynamically build the correct form for each model.

`POST /api/assess` - accepts a model ID and a list of tasks with their parameters. Returns cumulative damage, probability, probability label, and per-task damage breakdown. This is the only endpoint that performs calculations.

## Tasks

Ordered by dependency. Each task produces a working, testable increment.

### Task 1: API server

Create a FastAPI app that imports `fatigue_calc.py` and exposes two endpoints:

- `GET /api/models` returns model metadata and field definitions
- `POST /api/assess` accepts a model name and task list, returns assessment results

Verify with curl. No frontend yet.

Acceptance criteria:

- Server starts with `python app.py`
- `GET /api/models` returns all three models with correct field definitions
- `POST /api/assess` returns correct results for each model (verify against CLI output)
- Invalid model name returns 400
- Missing or invalid task parameters return 400 with a useful error message

### Task 2: Model selector UI

Create `static/index.html` with three clickable cards for model selection. Served by FastAPI as a static file.

Acceptance criteria:

- Page loads at `http://localhost:8000`
- Three cards displayed: LiFFT, DUET, Shoulder Tool
- Each card shows the model name and a short description
- Clicking a card visually highlights it as selected
- Model metadata is fetched from `/api/models`, not hardcoded

### Task 3: Task input form

Add a dynamic form below the model selector. The form fields change based on which model is selected, driven by the field definitions from `/api/models`.

Acceptance criteria:

- Selecting a model shows the correct input fields for that model
- User can fill in fields and click "Add Task" to add it to a task list below
- Each task in the list shows a summary of its inputs
- Tasks can be deleted from the list
- Task list persists when switching between models (but only tasks for the current model are shown - or all tasks are cleared on model switch; either is acceptable for now)

### Task 4: Live results

Call `POST /api/assess` whenever the task list changes and display results to the right of (or below) the task input.

Acceptance criteria:

- Results update automatically when tasks are added or removed (no submit button)
- Cumulative damage value is displayed
- Probability percentage is displayed
- Per-task breakdown is displayed showing each task's damage and percentage of total
- Empty task list shows zeroed-out results or a prompt to add tasks

### Task 5: Probability gauge

Add a visual gauge for the probability value. Color-coded by risk level.

Acceptance criteria:

- Gauge displays the probability as a visual element (semicircle, horizontal bar, or similar)
- Green when probability < 25%
- Yellow when probability is 25-50%
- Red when probability > 50%
- Gauge animates or transitions smoothly when the value changes
- The numeric percentage is still displayed alongside the gauge

### Task 6: Damage breakdown chart

Add a visual chart showing each task's contribution to total damage.

Acceptance criteria:

- Horizontal stacked bar or individual bars showing each task's proportion of total damage
- Tasks are labeled with their name and percentage
- Chart updates live as tasks change
- The highest-damage task is visually prominent

### Task 7: Scenario comparison

Add the ability to save a baseline scenario and compare it against a modified version.

Acceptance criteria:

- A "Save as Baseline" button snapshots the current tasks and results
- Once saved, the baseline results are shown on the left, the current (editable) results on the right
- Change in cumulative damage is displayed (absolute value and percentage change)
- Change in probability is displayed (absolute difference in percentage points)
- Decreases are shown in green, increases in red
- A "Clear Baseline" button returns to single-scenario mode
- The baseline is display-only; only the current scenario is editable

## Out of Scope

These are things we are explicitly not building now:

- User accounts or saved assessments
- PDF report generation
- Mobile-optimized layout
- Unit conversion (imperial/metric toggle)
- Exo-LiFFT exoskeleton extension
- Multiple shoulder outcome models (FTOV only)
- Bilateral task weight distribution for the Shoulder Tool
