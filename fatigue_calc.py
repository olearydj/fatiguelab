#!/usr/bin/env python3
"""
Fatigue failure risk assessment calculator.

Implements musculoskeletal disorder risk models based on fatigue failure theory
developed by Gallagher, Sesek, Schall et al. at Auburn University.
"""

import argparse
import math
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Base classes
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single work task with its parameters."""
    name: str
    params: dict


@dataclass
class TaskResult:
    """Result of analyzing a single task."""
    name: str
    damage: float
    pct_total: float


@dataclass
class AssessmentResult:
    """Full assessment result across all tasks."""
    model_name: str
    tasks: list[TaskResult]
    cumulative_damage: float
    probability: float
    probability_label: str


class FatigueModel(ABC):
    """Base class for fatigue failure risk models."""

    name: str
    description: str

    @abstractmethod
    def damage_per_cycle(self, **params) -> float:
        """Calculate damage per cycle for given task parameters."""

    @abstractmethod
    def task_damage(self, task: Task) -> float:
        """Calculate total damage for a task (DPC × reps)."""

    @abstractmethod
    def probability(self, cumulative_damage: float) -> float:
        """Convert cumulative damage to risk probability."""

    @property
    @abstractmethod
    def probability_label(self) -> str:
        """Human-readable label for what the probability represents."""

    def assess(self, tasks: list[Task]) -> AssessmentResult:
        """Run a full multi-task assessment."""
        damages = []
        for task in tasks:
            d = self.task_damage(task)
            damages.append((task.name, d))

        cd = sum(d for _, d in damages)

        task_results = [
            TaskResult(
                name=name,
                damage=d,
                pct_total=(d / cd * 100) if cd > 0 else 0,
            )
            for name, d in damages
        ]

        return AssessmentResult(
            model_name=self.name,
            tasks=task_results,
            cumulative_damage=cd,
            probability=self.probability(cd) if cd > 0 else 0,
            probability_label=self.probability_label,
        )


# ---------------------------------------------------------------------------
# LiFFT Model
# ---------------------------------------------------------------------------

class LiFFT(FatigueModel):
    """
    Lifting Fatigue Failure Tool (LiFFT).

    Estimates cumulative low back loading and probability of a high-risk job
    based on spinal motion segment fatigue data.

    Inputs per task:
        load_kg:     Weight of load (kg)
        distance_m:  Max horizontal distance from spine to load (m)
        reps:        Number of repetitions per workday

    References:
        Gallagher et al. (2017) Applied Ergonomics 63:142-150
    """

    name = "LiFFT"
    description = "Lifting Fatigue Failure Tool - low back disorder risk"

    SCALAR = 1_902_416
    MOMENT_COEFF = 0.038
    OFFSET = 0.32
    LOGISTIC_INTERCEPT = 1.72
    LOGISTIC_SLOPE = 1.03

    def damage_per_cycle(self, load_kg: float, distance_m: float, **_) -> float:
        moment_nm = load_kg * 9.81 * distance_m
        return math.exp(self.MOMENT_COEFF * moment_nm + self.OFFSET) / self.SCALAR

    def task_damage(self, task: Task) -> float:
        dpc = self.damage_per_cycle(
            load_kg=task.params["load_kg"],
            distance_m=task.params["distance_m"],
        )
        return dpc * task.params["reps"]

    def probability(self, cumulative_damage: float) -> float:
        if cumulative_damage <= 0:
            return 0.0
        y = self.LOGISTIC_INTERCEPT + self.LOGISTIC_SLOPE * math.log10(cumulative_damage)
        return math.exp(y) / (1 + math.exp(y))

    @property
    def probability_label(self) -> str:
        return "Probability of high-risk job (≥12 injuries per 200k hours)"


# ---------------------------------------------------------------------------
# Shared: Tendon S-N Curve (Schechtman & Bader 1997)
# ---------------------------------------------------------------------------

def tendon_cycles_to_failure(stress_pct_uts: float) -> float:
    """Median cycles to failure from the tendon S-N curve.

    S = 101.25 - 14.83 * log10(N)
    => N = 10^((101.25 - S) / 14.83)

    Args:
        stress_pct_uts: Stress as percentage of ultimate tensile strength (0-100).

    Returns:
        Median number of cycles to failure. Returns inf for stress <= 0.
    """
    if stress_pct_uts <= 0:
        return float("inf")
    if stress_pct_uts >= 101.25:
        return 1.0
    return 10 ** ((101.25 - stress_pct_uts) / 14.83)


def tendon_dpc(stress_pct_uts: float) -> float:
    """Damage per cycle from the tendon S-N curve."""
    n = tendon_cycles_to_failure(stress_pct_uts)
    if math.isinf(n):
        return 0.0
    return 1.0 / n


# ---------------------------------------------------------------------------
# DUET Model
# ---------------------------------------------------------------------------

class DUET(FatigueModel):
    """
    Distal Upper Extremity Tool (DUET).

    Estimates cumulative damage and probability of distal upper extremity
    disorders based on tendon fatigue failure theory.

    Inputs per task:
        omni:  OMNI-RES effort rating (0-10)
        reps:  Number of repetitions per workday

    References:
        Gallagher et al. (2018) Human Factors 60(8):1146-1162
    """

    name = "DUET"
    description = "Distal Upper Extremity Tool - hand/wrist/forearm disorder risk"

    LOGISTIC_INTERCEPT = 0.766
    LOGISTIC_SLOPE = 1.515

    def damage_per_cycle(self, omni: int, **_) -> float:
        stress_pct = omni * 10  # Each OMNI point = 10% UTS
        return tendon_dpc(stress_pct)

    def task_damage(self, task: Task) -> float:
        dpc = self.damage_per_cycle(omni=task.params["omni"])
        return dpc * task.params["reps"]

    def probability(self, cumulative_damage: float) -> float:
        if cumulative_damage <= 0:
            return 0.0
        y = self.LOGISTIC_INTERCEPT + self.LOGISTIC_SLOPE * math.log10(cumulative_damage)
        return math.exp(y) / (1 + math.exp(y))

    @property
    def probability_label(self) -> str:
        return "Probability of distal upper extremity outcome"


# ---------------------------------------------------------------------------
# Shoulder Tool Model
# ---------------------------------------------------------------------------

class ShoulderTool(FatigueModel):
    """
    Shoulder Tool.

    Estimates cumulative shoulder damage and probability of shoulder MSD
    based on tendon fatigue failure theory.

    Inputs per task:
        load_lb:      Weight held or force exerted (lb)
        distance_in:  Horizontal distance from acromion to load center (in)
        reps:         Number of repetitions per workday
        task_type:    "handling" (default), "push_pull", or "push_down"

    References:
        Bani Hani et al. (2021) Ergonomics 64(1):39-54
    """

    name = "Shoulder Tool"
    description = "Shoulder Tool - shoulder disorder risk"

    SHOULDER_STRENGTH_IN_LB = 681  # 3DSSPP 50th percentile male, in-lb
    ARM_WEIGHT_LB = 8.6  # Estimated arm weight

    LOGISTIC_INTERCEPT = 0.870
    LOGISTIC_SLOPE = 0.932

    def shoulder_moment(self, load_lb: float, distance_in: float,
                        task_type: str = "handling") -> float:
        """Calculate shoulder moment in in-lb."""
        if task_type == "handling":
            return load_lb * distance_in + self.ARM_WEIGHT_LB * distance_in / 2
        else:  # push_pull or push_down
            return load_lb * distance_in

    def damage_per_cycle(self, load_lb: float, distance_in: float,
                         task_type: str = "handling", **_) -> float:
        moment = self.shoulder_moment(load_lb, distance_in, task_type)
        stress_pct = (moment / self.SHOULDER_STRENGTH_IN_LB) * 100
        return tendon_dpc(stress_pct)

    def task_damage(self, task: Task) -> float:
        dpc = self.damage_per_cycle(
            load_lb=task.params["load_lb"],
            distance_in=task.params["distance_in"],
            task_type=task.params.get("task_type", "handling"),
        )
        return dpc * task.params["reps"]

    def probability(self, cumulative_damage: float) -> float:
        if cumulative_damage <= 0:
            return 0.0
        y = self.LOGISTIC_INTERCEPT + self.LOGISTIC_SLOPE * math.log10(cumulative_damage)
        return math.exp(y) / (1 + math.exp(y))

    @property
    def probability_label(self) -> str:
        return "Probability of shoulder MSD (FTOV)"


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

MODELS = {
    "lifft": LiFFT,
    "duet": DUET,
    "shoulder": ShoulderTool,
}


def get_model(name: str) -> FatigueModel:
    cls = MODELS.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown model: {name}. Available: {', '.join(MODELS)}")
    return cls()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
        lines.append(f"  {DIM}{'-'*20} {'-'*12} {'-'*10}{RESET}")
        for t in result.tasks:
            bar_len = int(t.pct_total / 5)  # max 20 chars at 100%
            bar = "█" * bar_len
            lines.append(
                f"  {WHITE}{t.name:<20}{RESET} {t.damage:>12.6f} {YELLOW}{t.pct_total:>8.1f}%{RESET} {DIM}{bar}{RESET}"
            )
        lines.append(f"  {DIM}{'-'*20} {'-'*12} {'-'*10}{RESET}")
    else:
        lines.append("")

    lines.append(f"  Cumulative Damage:  {BOLD}{result.cumulative_damage:.6f}{RESET}")
    lines.append(f"  {DIM}{result.probability_label}:{RESET}")
    lines.append(f"  {BOLD}{risk_color}{pct:.1f}%{RESET}")
    lines.append(f"{DIM}{'=' * 60}{RESET}\n")
    return "\n".join(lines)


def parse_tasks_lifft(args) -> list[Task]:
    """Parse LiFFT task arguments.

    Accepts repeated --task flags in the form:
        --task LOAD_KG,DISTANCE_M,REPS[,NAME]
    """
    tasks = []
    for i, spec in enumerate(args.task):
        parts = spec.split(",")
        if len(parts) < 3:
            print(f"Error: task needs at least 3 values: LOAD_KG,DISTANCE_M,REPS", file=sys.stderr)
            sys.exit(1)
        name = parts[3] if len(parts) > 3 else f"Task {i + 1}"
        tasks.append(Task(
            name=name,
            params={
                "load_kg": float(parts[0]),
                "distance_m": float(parts[1]),
                "reps": int(parts[2]),
            },
        ))
    return tasks


def parse_tasks_duet(args) -> list[Task]:
    """Parse DUET task arguments.

    Accepts repeated --task flags in the form:
        --task OMNI,REPS[,NAME]
    """
    tasks = []
    for i, spec in enumerate(args.task):
        parts = spec.split(",")
        if len(parts) < 2:
            print("Error: task needs at least 2 values: OMNI,REPS", file=sys.stderr)
            sys.exit(1)
        name = parts[2] if len(parts) > 2 else f"Task {i + 1}"
        tasks.append(Task(
            name=name,
            params={
                "omni": int(parts[0]),
                "reps": int(parts[1]),
            },
        ))
    return tasks


def parse_tasks_shoulder(args) -> list[Task]:
    """Parse Shoulder Tool task arguments.

    Accepts repeated --task flags in the form:
        --task LOAD_LB,DISTANCE_IN,REPS[,NAME]

    Use --task-type to override task type (default: handling).
    """
    task_type = getattr(args, "task_type", None) or "handling"
    tasks = []
    for i, spec in enumerate(args.task):
        parts = spec.split(",")
        if len(parts) < 3:
            print("Error: task needs at least 3 values: LOAD_LB,DISTANCE_IN,REPS", file=sys.stderr)
            sys.exit(1)
        name = parts[3] if len(parts) > 3 else f"Task {i + 1}"
        tasks.append(Task(
            name=name,
            params={
                "load_lb": float(parts[0]),
                "distance_in": float(parts[1]),
                "reps": int(parts[2]),
                "task_type": task_type,
            },
        ))
    return tasks


TASK_PARSERS = {
    "lifft": parse_tasks_lifft,
    "duet": parse_tasks_duet,
    "shoulder": parse_tasks_shoulder,
}


def main():
    parser = argparse.ArgumentParser(
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
    parser.add_argument("--task", "-t", action="append", help="Task spec (varies by model)")
    parser.add_argument("--task-type", choices=["handling", "push_pull", "push_down"],
                        default="handling", help="Shoulder tool task type (default: handling)")
    parser.add_argument("--list", "-l", action="store_true", help="List available models")

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
