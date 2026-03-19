"""
Fatigue failure risk assessment models.

Implements musculoskeletal disorder risk models based on fatigue failure theory
developed by Gallagher, Sesek, Schall et al. at Auburn University.
"""

import math
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
    def task_damage(self, task: Task) -> float:
        """Calculate total damage for a task (DPC x reps)."""

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
        y = self.LOGISTIC_INTERCEPT + self.LOGISTIC_SLOPE * math.log10(
            cumulative_damage
        )
        return math.exp(y) / (1 + math.exp(y))

    @property
    def probability_label(self) -> str:
        return "Probability of high-risk job (>=12 injuries per 200k hours)"


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
        y = self.LOGISTIC_INTERCEPT + self.LOGISTIC_SLOPE * math.log10(
            cumulative_damage
        )
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

    def shoulder_moment(
        self, load_lb: float, distance_in: float, task_type: str = "handling"
    ) -> float:
        """Calculate shoulder moment in in-lb."""
        if task_type == "handling":
            return load_lb * distance_in + self.ARM_WEIGHT_LB * distance_in / 2
        else:  # push_pull or push_down
            return load_lb * distance_in

    def damage_per_cycle(
        self, load_lb: float, distance_in: float, task_type: str = "handling", **_
    ) -> float:
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
        y = self.LOGISTIC_INTERCEPT + self.LOGISTIC_SLOPE * math.log10(
            cumulative_damage
        )
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
# CLI task parsers
# ---------------------------------------------------------------------------


def parse_tasks_lifft(args) -> list[Task]:
    """Parse LiFFT task arguments: --task LOAD_KG,DISTANCE_M,REPS[,NAME]"""
    import sys

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


def parse_tasks_duet(args) -> list[Task]:
    """Parse DUET task arguments: --task OMNI,REPS[,NAME]"""
    import sys

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


def parse_tasks_shoulder(args) -> list[Task]:
    """Parse Shoulder Tool task arguments: --task LOAD_LB,DISTANCE_IN,REPS[,NAME]"""
    import sys

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
    "lifft": parse_tasks_lifft,
    "duet": parse_tasks_duet,
    "shoulder": parse_tasks_shoulder,
}
