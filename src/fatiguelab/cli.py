"""Command-line interface for the fatigue failure risk calculator."""

import argparse
import sys

from .models import AssessmentResult, Task, get_model, MODELS


# ---------------------------------------------------------------------------
# Task argument parsers
# ---------------------------------------------------------------------------


def _parse_tasks_lifft(args) -> list[Task]:
    """Parse LiFFT task arguments: --task LOAD_KG,DISTANCE_M,REPS[,NAME]"""
    tasks = []
    for i, spec in enumerate(args.task):
        parts = spec.split(",")
        if len(parts) < 3:
            print(
                "Error: task needs at least 3 values: LOAD_KG,DISTANCE_M,REPS",
                file=sys.stderr,
            )
            sys.exit(1)
        name = parts[3] if len(parts) > 3 else f"Task {i + 1}"
        tasks.append(
            Task(
                name=name,
                params={
                    "load_kg": float(parts[0]),
                    "distance_m": float(parts[1]),
                    "reps": int(parts[2]),
                },
            )
        )
    return tasks


def _parse_tasks_duet(args) -> list[Task]:
    """Parse DUET task arguments: --task OMNI,REPS[,NAME]"""
    tasks = []
    for i, spec in enumerate(args.task):
        parts = spec.split(",")
        if len(parts) < 2:
            print("Error: task needs at least 2 values: OMNI,REPS", file=sys.stderr)
            sys.exit(1)
        name = parts[2] if len(parts) > 2 else f"Task {i + 1}"
        tasks.append(
            Task(
                name=name,
                params={
                    "omni": int(parts[0]),
                    "reps": int(parts[1]),
                },
            )
        )
    return tasks


def _parse_tasks_shoulder(args) -> list[Task]:
    """Parse Shoulder Tool task arguments: --task LOAD_LB,DISTANCE_IN,REPS[,NAME]"""
    task_type = getattr(args, "task_type", None) or "handling"
    tasks = []
    for i, spec in enumerate(args.task):
        parts = spec.split(",")
        if len(parts) < 3:
            print(
                "Error: task needs at least 3 values: LOAD_LB,DISTANCE_IN,REPS",
                file=sys.stderr,
            )
            sys.exit(1)
        name = parts[3] if len(parts) > 3 else f"Task {i + 1}"
        tasks.append(
            Task(
                name=name,
                params={
                    "load_lb": float(parts[0]),
                    "distance_in": float(parts[1]),
                    "reps": int(parts[2]),
                    "task_type": task_type,
                },
            )
        )
    return tasks


TASK_PARSERS = {
    "lifft": _parse_tasks_lifft,
    "duet": _parse_tasks_duet,
    "shoulder": _parse_tasks_shoulder,
}


def _use_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def format_result(result: AssessmentResult) -> str:
    color = _use_color()

    # ANSI codes
    RESET = "\033[0m" if color else ""
    BOLD = "\033[1m" if color else ""
    DIM = "\033[2m" if color else ""
    CYAN = "\033[36m" if color else ""
    YELLOW = "\033[33m" if color else ""
    GREEN = "\033[32m" if color else ""
    RED = "\033[31m" if color else ""
    WHITE = "\033[97m" if color else ""

    pct = result.probability * 100
    if pct < 25:
        risk_color = GREEN
    elif pct < 50:
        risk_color = YELLOW
    else:
        risk_color = RED

    lines = []
    lines.append(f"\n{DIM}{'=' * 60}{RESET}")
    lines.append(f"  {BOLD}{CYAN}{result.model_name} Assessment{RESET}")
    lines.append(f"{DIM}{'=' * 60}{RESET}")

    if len(result.tasks) > 1:
        lines.append(f"\n  {DIM}{'Task':<20} {'Damage':>12} {'% Total':>10}{RESET}")
        lines.append(f"  {DIM}{'-' * 20} {'-' * 12} {'-' * 10}{RESET}")
        for t in result.tasks:
            bar_len = int(t.pct_total / 5)  # max 20 chars at 100%
            bar = "\u2588" * bar_len
            lines.append(
                f"  {WHITE}{t.name:<20}{RESET} {t.damage:>12.6f} {YELLOW}{t.pct_total:>8.1f}%{RESET} {DIM}{bar}{RESET}"
            )
        lines.append(f"  {DIM}{'-' * 20} {'-' * 12} {'-' * 10}{RESET}")
    else:
        lines.append("")

    lines.append(f"  Cumulative Damage:  {BOLD}{result.cumulative_damage:.6f}{RESET}")
    lines.append(f"  {DIM}{result.probability_label}:{RESET}")
    lines.append(f"  {BOLD}{risk_color}{pct:.1f}%{RESET}")
    lines.append(f"{DIM}{'=' * 60}{RESET}\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="fl",
        description="Fatigue failure MSD risk calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
LiFFT (low back) - task: LOAD_KG,DISTANCE_M,REPS[,NAME]
  %(prog)s lifft -t 10,0.4,500
  %(prog)s lifft -t 10,0.4,500,Palletizing -t 5,0.3,200,Stacking

DUET (hand/wrist/forearm) - task: OMNI_RATING,REPS[,NAME]
  %(prog)s duet -t 4,1350
  %(prog)s duet -t 4,1350,Gripping -t 6,500,Twisting

Shoulder Tool - task: LOAD_LB,DISTANCE_IN,REPS[,NAME]
  %(prog)s shoulder -t 2,16,2880
  %(prog)s shoulder -t 5,18,4800,Lifting -t 3,14,1200,Reaching
  %(prog)s shoulder --task-type push_pull -t 10,12,500,Pushing

Start the web app:
  %(prog)s serve
  %(prog)s serve --port 8080

Interactive demo walkthrough:
  %(prog)s demo

Show available models:
  %(prog)s --list
""",
    )
    parser.add_argument(
        "model", nargs="?", help="Model (lifft, duet, shoulder), 'serve', or 'demo'"
    )
    parser.add_argument(
        "--task", "-t", action="append", help="Task spec (varies by model)"
    )
    parser.add_argument(
        "--task-type",
        choices=["handling", "push_pull", "push_down"],
        default="handling",
        help="Shoulder tool task type (default: handling)",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available models"
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port for the web server (default: 8000)",
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable models:")
        for key, cls in MODELS.items():
            print(f"  {key:<10} {cls.description}")
        print()
        return

    if not args.model:
        color = _use_color()
        B = "\033[1m" if color else ""
        C = "\033[36m" if color else ""
        D = "\033[2m" if color else ""
        R = "\033[0m" if color else ""
        print(f"""
  {B}{C}fatiguelab{R} - MSD risk assessment using fatigue failure theory
  {D}Gallagher, Sesek, Schall et al. - Auburn University{R}
  {D}https://github.com/olearydj/fatiguelab{R}

  {B}Quick start:{R}
    fl demo                  Interactive walkthrough
    fl serve                 Web app at http://127.0.0.1:8000
    fl lifft -t 10,0.4,500   Run a LiFFT assessment

  {B}More info:{R}
    fl --help                Full usage and examples
    fl --list                Available models
""")
        return

    if args.model == "serve":
        import uvicorn

        from .api import app

        uvicorn.run(app, host="127.0.0.1", port=args.port)
        return

    if args.model == "demo":
        from .demo import run

        run()
        return

    if not args.task:
        print("Error: at least one --task is required", file=sys.stderr)
        sys.exit(1)

    model = get_model(args.model)
    parse_fn = TASK_PARSERS.get(args.model.lower())
    if parse_fn is None:
        print(f"Error: no task parser for model {args.model}", file=sys.stderr)
        sys.exit(1)

    tasks = parse_fn(args)
    result = model.assess(tasks)
    print(format_result(result))


if __name__ == "__main__":
    main()
