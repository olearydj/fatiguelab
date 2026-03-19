"""Command-line interface for the fatigue failure risk calculator."""

import argparse
import sys

from .models import AssessmentResult, get_model, MODELS, TASK_PARSERS


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

Show available models:
  %(prog)s --list
""",
    )
    parser.add_argument("model", nargs="?", help="Model to use (lifft)")
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

    args = parser.parse_args()

    if args.list:
        print("\nAvailable models:")
        for key, cls in MODELS.items():
            print(f"  {key:<10} {cls.description}")
        print()
        return

    if not args.model:
        parser.print_help()
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
