"""Interactive demo walkthrough of all three fatigue failure models."""

import os
import sys

from .cli import format_result
from .models import Task, get_model


def _color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(code):
    return f"\033[{code}m" if _color() else ""


BOLD = _c("1")
DIM = _c("2")
RESET = _c("0")
CYAN = _c("36")
YELLOW = _c("33")
MAGENTA = _c("35")


def header(title):
    print(f"\n{BOLD}{CYAN}{'━' * 60}{RESET}")
    print(f"  {BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'━' * 60}{RESET}\n")


def scenario(text):
    print(f"  {MAGENTA}Scenario:{RESET} {text}")


def detail(text):
    print(f"  {DIM}{text}{RESET}")


def insight(text):
    print(f"  {YELLOW}→ {text}{RESET}")


def assess(model_name, tasks):
    model = get_model(model_name)
    task_objs = [Task(name=name, params=params) for name, params in tasks]
    result = model.assess(task_objs)
    print(format_result(result))


def pause():
    print()
    try:
        input("  [enter to continue] ")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    if _color():
        os.system("clear" if os.name != "nt" else "cls")


def run():
    if _color():
        os.system("clear" if os.name != "nt" else "cls")

    header("Fatigue Failure MSD Risk Calculator")
    print("  This tool implements three musculoskeletal disorder risk")
    print(f"  assessment models based on {BOLD}fatigue failure theory{RESET}")
    print("  developed at Auburn University.")
    print()
    detail("Gallagher, Sesek, Schall et al.")
    detail("Applied to: low back, hand/wrist, and shoulder injuries")
    print()
    detail("The same physics that predicts metal fatigue in bridges")
    detail("predicts tissue damage from repetitive work.")
    pause()

    # ---- List models ----
    header("Available Models")
    from .models import MODELS

    print("\n  Available models:")
    for key, cls in MODELS.items():
        print(f"    {key:<10} {cls.description}")
    print()
    pause()

    # ---- LiFFT: Simple case ----
    header("LiFFT: Single Lifting Task")
    scenario("A warehouse worker lifts 15kg boxes from a pallet")
    detail("0.45m from their spine, 600 times per shift.")
    print()
    assess("lifft", [("Task 1", {"load_kg": 15, "distance_m": 0.45, "reps": 600})])
    pause()

    # ---- LiFFT: Multi-task ----
    header("LiFFT: Multi-Task Assessment")
    scenario("Same worker also does lighter picks and occasional heavy bag lifts.")
    print()
    assess(
        "lifft",
        [
            ("Palletizing", {"load_kg": 15, "distance_m": 0.45, "reps": 600}),
            ("Light picks", {"load_kg": 5, "distance_m": 0.3, "reps": 300}),
            ("Heavy bags", {"load_kg": 25, "distance_m": 0.55, "reps": 80}),
        ],
    )
    insight("Heavy bags are only 80 reps but dominate the damage")
    insight("due to the high load (25kg) and reach distance (0.55m).")
    pause()

    # ---- DUET: Assembly line ----
    header("DUET: Assembly Line Hand/Wrist Assessment")
    scenario(
        "An electronics assembler performs three tasks at different effort levels:"
    )
    detail("Inserting connectors (easy, OMNI 3):     2000 reps/day")
    detail("Tightening screws (moderate, OMNI 5):     800 reps/day")
    detail("Crimping cables (hard, OMNI 8):           150 reps/day")
    print()
    assess(
        "duet",
        [
            ("Connectors", {"omni": 3, "reps": 2000}),
            ("Screws", {"omni": 5, "reps": 800}),
            ("Crimping", {"omni": 8, "reps": 150}),
        ],
    )
    insight("Even with only 150 reps, the hard crimping task")
    insight("drives the majority of cumulative damage.")
    pause()

    # ---- DUET: What-if ----
    header("DUET: What-If — Tool Assists")
    scenario("What if we introduce power tools to reduce exertion?")
    detail("Power screwdriver: OMNI 5 → 2")
    detail("Powered crimper:   OMNI 8 → 4")
    print()
    print(f"  {DIM}Before:{RESET}")
    assess(
        "duet",
        [
            ("Connectors", {"omni": 3, "reps": 2000}),
            ("Screws", {"omni": 5, "reps": 800}),
            ("Crimping", {"omni": 8, "reps": 150}),
        ],
    )
    print(f"  {DIM}After:{RESET}")
    assess(
        "duet",
        [
            ("Connectors", {"omni": 3, "reps": 2000}),
            ("Screws (powered)", {"omni": 2, "reps": 800}),
            ("Crimping (powered)", {"omni": 4, "reps": 150}),
        ],
    )
    insight("Targeted tool assists on high-effort tasks yield")
    insight("dramatic reductions in cumulative damage and risk.")
    pause()

    # ---- Shoulder: Overhead work ----
    header("Shoulder Tool: Overhead Shelf Stocking")
    scenario("A retail worker stocks shelves, reaching out 20in")
    detail("with 3lb items, 1500 times per shift.")
    print()
    assess(
        "shoulder",
        [
            ("Stocking", {"load_lb": 3, "distance_in": 20, "reps": 1500}),
        ],
    )
    pause()

    # ---- Shoulder: Push/pull comparison ----
    header("Shoulder Tool: Handling vs Push/Pull")
    scenario("Compare stocking (handling) vs cart pushing (push/pull).")
    detail("Handling includes arm weight in the moment calculation.")
    detail("Push/pull does not.")
    print()
    print(f"  {DIM}Shelf stocking (handling, 3lb at 20in, 1500 reps):{RESET}")
    assess(
        "shoulder",
        [
            ("Stocking", {"load_lb": 3, "distance_in": 20, "reps": 1500}),
        ],
    )
    print(f"  {DIM}Cart pushing (push_pull, 10lb at 12in, 200 reps):{RESET}")
    assess(
        "shoulder",
        [
            (
                "Cart pushing",
                {
                    "load_lb": 10,
                    "distance_in": 12,
                    "reps": 200,
                    "task_type": "push_pull",
                },
            ),
        ],
    )
    insight("Different task types use different biomechanical models")
    insight("for how force translates to shoulder moment.")
    pause()

    # ---- Summary ----
    header("Summary")
    print(f"  {BOLD}Three models, one framework:{RESET}")
    print(f"    {CYAN}lifft{RESET}     Low back injury risk from lifting")
    print(
        f"    {CYAN}duet{RESET}      Hand/wrist/forearm risk from repetitive exertion"
    )
    print(f"    {CYAN}shoulder{RESET}  Shoulder risk from reaching/handling")
    print()
    print(f"  {BOLD}Core principle:{RESET}")
    print("  Cumulative micro-damage from repeated loading predicts")
    print("  injury risk — just like metal fatigue predicts structural failure.")
    print()
    print(f"  {BOLD}Practical insight:{RESET}")
    print("  A few high-force exertions often cause more damage than")
    print("  many low-force ones. Target interventions at the highest-")
    print("  damage tasks for the biggest risk reductions.")
    print()
    print(f"{DIM}{'━' * 60}{RESET}")
