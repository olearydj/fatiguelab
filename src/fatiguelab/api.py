"""
Web API for the fatigue failure risk calculator.
Thin wrapper over models.py - all math lives there.
"""

from importlib.resources import files

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .models import Task, get_model, MODELS

app = FastAPI(title="Fatigue Failure Risk Calculator")

# ---------------------------------------------------------------------------
# API models
# ---------------------------------------------------------------------------

FIELD_DEFINITIONS = {
    "lifft": [
        {
            "name": "load_kg",
            "label": "Load (kg)",
            "type": "number",
            "min": 0,
            "step": 0.1,
        },
        {
            "name": "distance_m",
            "label": "Horizontal Distance from Spine (m)",
            "type": "number",
            "min": 0,
            "step": 0.01,
        },
        {
            "name": "reps",
            "label": "Repetitions per Workday",
            "type": "number",
            "min": 0,
            "step": 1,
        },
    ],
    "duet": [
        {
            "name": "omni",
            "label": "OMNI-RES Effort Rating",
            "type": "select",
            "options": [
                {"value": 0, "label": "0 - Extremely Easy"},
                {"value": 1, "label": "1"},
                {"value": 2, "label": "2 - Easy"},
                {"value": 3, "label": "3"},
                {"value": 4, "label": "4 - Somewhat Easy"},
                {"value": 5, "label": "5"},
                {"value": 6, "label": "6 - Somewhat Hard"},
                {"value": 7, "label": "7"},
                {"value": 8, "label": "8 - Hard"},
                {"value": 9, "label": "9"},
                {"value": 10, "label": "10 - Extremely Hard"},
            ],
        },
        {
            "name": "reps",
            "label": "Repetitions per Workday",
            "type": "number",
            "min": 0,
            "step": 1,
        },
    ],
    "shoulder": [
        {
            "name": "load_lb",
            "label": "Load / Force (lb)",
            "type": "number",
            "min": 0,
            "step": 0.1,
        },
        {
            "name": "distance_in",
            "label": "Distance from Acromion (in)",
            "type": "number",
            "min": 0,
            "step": 0.1,
        },
        {
            "name": "reps",
            "label": "Repetitions per Workday",
            "type": "number",
            "min": 0,
            "step": 1,
        },
        {
            "name": "task_type",
            "label": "Task Type",
            "type": "select",
            "options": [
                {"value": "handling", "label": "Handling Loads"},
                {"value": "push_pull", "label": "Horizontal Push/Pull"},
                {"value": "push_down", "label": "Push/Pull Downward"},
            ],
        },
    ],
}


class TaskInput(BaseModel):
    name: str = "Task"
    params: dict


class AssessRequest(BaseModel):
    model: str
    tasks: list[TaskInput]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/models")
def list_models():
    return {
        "models": [
            {
                "id": key,
                "name": cls.name,
                "description": cls.description,
                "fields": FIELD_DEFINITIONS[key],
            }
            for key, cls in MODELS.items()
        ]
    }


@app.post("/api/assess")
def assess(req: AssessRequest):
    try:
        model = get_model(req.model)
    except ValueError:
        raise HTTPException(
            400, f"Unknown model: {req.model}. Available: {', '.join(MODELS)}"
        )

    if not req.tasks:
        return {
            "model": model.name,
            "cumulative_damage": 0,
            "probability": 0,
            "probability_label": model.probability_label,
            "tasks": [],
        }

    tasks = [Task(name=t.name, params=t.params) for t in req.tasks]

    try:
        result = model.assess(tasks)
    except (KeyError, TypeError, ValueError) as e:
        raise HTTPException(400, f"Invalid task parameters: {e}")

    return {
        "model": result.model_name,
        "cumulative_damage": result.cumulative_damage,
        "probability": result.probability,
        "probability_label": result.probability_label,
        "tasks": [
            {"name": t.name, "damage": t.damage, "pct_total": t.pct_total}
            for t in result.tasks
        ],
    }


# ---------------------------------------------------------------------------
# Static files and SPA fallback
# ---------------------------------------------------------------------------

static_dir = files("fatiguelab") / "static"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def index():
    return FileResponse(str(static_dir / "index.html"))
