"""Tests for fatigue failure risk models."""

import math
import subprocess
import sys

import pytest

from fatiguelab.models import (
    LiFFT,
    DUET,
    ShoulderTool,
    Task,
    get_model,
    MODELS,
    tendon_cycles_to_failure,
    tendon_dpc,
)


# ---------------------------------------------------------------------------
# Shared tendon S-N curve
# ---------------------------------------------------------------------------


class TestTendonSNCurve:
    def test_known_values(self):
        """Verify against published data points from Schechtman & Bader 1997."""
        # At 20% UTS, ~300,000 cycles (widely cited)
        n = tendon_cycles_to_failure(20)
        assert 280_000 < n < 330_000

        # At 50% UTS, ~2,900 cycles
        n = tendon_cycles_to_failure(50)
        assert 2_500 < n < 3_500

    def test_zero_stress_returns_inf(self):
        assert tendon_cycles_to_failure(0) == float("inf")

    def test_negative_stress_returns_inf(self):
        assert tendon_cycles_to_failure(-10) == float("inf")

    def test_100_pct_stress(self):
        n = tendon_cycles_to_failure(100)
        assert n == pytest.approx(10 ** (1.25 / 14.83))

    def test_over_100_pct_returns_1(self):
        assert tendon_cycles_to_failure(102) == 1.0

    def test_monotonically_decreasing(self):
        """Higher stress = fewer cycles to failure."""
        prev = float("inf")
        for s in range(10, 100, 10):
            n = tendon_cycles_to_failure(s)
            assert n < prev
            prev = n

    def test_dpc_zero_stress(self):
        assert tendon_dpc(0) == 0.0

    def test_dpc_is_inverse_of_cycles(self):
        for s in [20, 40, 60, 80]:
            assert tendon_dpc(s) == pytest.approx(1.0 / tendon_cycles_to_failure(s))


# ---------------------------------------------------------------------------
# LiFFT unit tests
# ---------------------------------------------------------------------------


class TestLiFFTDamagePerCycle:
    def setup_method(self):
        self.model = LiFFT()

    def test_zero_load(self):
        dpc = self.model.damage_per_cycle(load_kg=0, distance_m=0.4)
        expected = math.exp(0.32) / 1_902_416
        assert dpc == pytest.approx(expected)

    def test_zero_distance(self):
        dpc = self.model.damage_per_cycle(load_kg=10, distance_m=0)
        expected = math.exp(0.32) / 1_902_416
        assert dpc == pytest.approx(expected)

    def test_known_moment(self):
        """10kg at 0.5m = 49.05 Nm moment."""
        moment = 10 * 9.81 * 0.5
        dpc = self.model.damage_per_cycle(load_kg=10, distance_m=0.5)
        expected = math.exp(0.038 * moment + 0.32) / 1_902_416
        assert dpc == pytest.approx(expected)

    def test_damage_increases_with_load(self):
        dpc_light = self.model.damage_per_cycle(load_kg=5, distance_m=0.4)
        dpc_heavy = self.model.damage_per_cycle(load_kg=20, distance_m=0.4)
        assert dpc_heavy > dpc_light

    def test_damage_increases_with_distance(self):
        dpc_close = self.model.damage_per_cycle(load_kg=10, distance_m=0.2)
        dpc_far = self.model.damage_per_cycle(load_kg=10, distance_m=0.6)
        assert dpc_far > dpc_close


class TestLiFFTTaskDamage:
    def setup_method(self):
        self.model = LiFFT()

    def test_scales_with_reps(self):
        task_100 = Task(
            name="a", params={"load_kg": 10, "distance_m": 0.4, "reps": 100}
        )
        task_500 = Task(
            name="b", params={"load_kg": 10, "distance_m": 0.4, "reps": 500}
        )
        assert self.model.task_damage(task_500) == pytest.approx(
            self.model.task_damage(task_100) * 5
        )

    def test_zero_reps(self):
        task = Task(name="none", params={"load_kg": 10, "distance_m": 0.4, "reps": 0})
        assert self.model.task_damage(task) == 0.0


class TestLiFFTProbability:
    def setup_method(self):
        self.model = LiFFT()

    def test_zero_damage(self):
        assert self.model.probability(0) == 0.0

    def test_output_is_between_0_and_1(self):
        for cd in [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0]:
            p = self.model.probability(cd)
            assert 0 < p < 1, f"probability({cd}) = {p}"

    def test_increases_with_damage(self):
        p_low = self.model.probability(0.001)
        p_high = self.model.probability(1.0)
        assert p_high > p_low

    def test_logistic_formula(self):
        cd = 0.05
        y = 1.72 + 1.03 * math.log10(cd)
        expected = math.exp(y) / (1 + math.exp(y))
        assert self.model.probability(cd) == pytest.approx(expected)


class TestLiFFTAssessment:
    def setup_method(self):
        self.model = LiFFT()

    def test_single_task_pct_is_100(self):
        tasks = [
            Task(name="only", params={"load_kg": 10, "distance_m": 0.4, "reps": 500})
        ]
        result = self.model.assess(tasks)
        assert result.tasks[0].pct_total == pytest.approx(100.0)

    def test_multi_task_pcts_sum_to_100(self):
        tasks = [
            Task(name="a", params={"load_kg": 10, "distance_m": 0.4, "reps": 500}),
            Task(name="b", params={"load_kg": 5, "distance_m": 0.3, "reps": 200}),
            Task(name="c", params={"load_kg": 20, "distance_m": 0.5, "reps": 100}),
        ]
        result = self.model.assess(tasks)
        total_pct = sum(t.pct_total for t in result.tasks)
        assert total_pct == pytest.approx(100.0)

    def test_cumulative_damage_is_sum_of_tasks(self):
        tasks = [
            Task(name="a", params={"load_kg": 10, "distance_m": 0.4, "reps": 500}),
            Task(name="b", params={"load_kg": 5, "distance_m": 0.3, "reps": 200}),
        ]
        result = self.model.assess(tasks)
        expected_cd = sum(t.damage for t in result.tasks)
        assert result.cumulative_damage == pytest.approx(expected_cd)

    def test_empty_tasks(self):
        result = self.model.assess([])
        assert result.cumulative_damage == 0.0
        assert result.probability == 0


# ---------------------------------------------------------------------------
# DUET unit tests
# ---------------------------------------------------------------------------


class TestDUETDamagePerCycle:
    def setup_method(self):
        self.model = DUET()

    def test_omni_0_is_zero_damage(self):
        assert self.model.damage_per_cycle(omni=0) == 0.0

    def test_omni_4_matches_published(self):
        """OMNI 4 = 40% UTS. N = 10^((101.25-40)/14.83) ~ 13,499."""
        dpc = self.model.damage_per_cycle(omni=4)
        expected = 1.0 / 10 ** ((101.25 - 40) / 14.83)
        assert dpc == pytest.approx(expected)

    def test_damage_increases_with_omni(self):
        for omni in range(1, 10):
            assert self.model.damage_per_cycle(
                omni=omni + 1
            ) > self.model.damage_per_cycle(omni=omni)

    def test_known_dpc_values(self):
        """Verify against precomputed DPC table from research."""
        expected = {
            1: 7.03e-7,
            2: 3.32e-6,
            3: 1.57e-5,
            4: 7.41e-5,
            5: 3.50e-4,
            6: 1.65e-3,
            7: 7.81e-3,
            8: 3.69e-2,
            9: 1.74e-1,
        }
        for omni, exp_dpc in expected.items():
            dpc = self.model.damage_per_cycle(omni=omni)
            assert dpc == pytest.approx(exp_dpc, rel=0.02), (
                f"OMNI {omni}: {dpc} != {exp_dpc}"
            )


class TestDUETPublishedExamples:
    """Verify against published example outputs from the DUET web tool."""

    def setup_method(self):
        self.model = DUET()

    def test_mono_task_omni4_1350reps(self):
        """Published: OMNI=4, 1350 reps -> CD=0.1000, P=32.1%."""
        tasks = [Task(name="test", params={"omni": 4, "reps": 1350})]
        result = self.model.assess(tasks)
        assert result.cumulative_damage == pytest.approx(0.1000, rel=0.02)
        assert result.probability * 100 == pytest.approx(32.1, abs=1.0)

    def test_multi_task_probability(self):
        """Published: multi-task CD=0.597 -> P~60.5%."""
        cd = 0.597
        p = self.model.probability(cd)
        assert p * 100 == pytest.approx(60.5, abs=1.5)


class TestDUETTaskDamage:
    def setup_method(self):
        self.model = DUET()

    def test_scales_with_reps(self):
        task_100 = Task(name="a", params={"omni": 5, "reps": 100})
        task_300 = Task(name="b", params={"omni": 5, "reps": 300})
        assert self.model.task_damage(task_300) == pytest.approx(
            self.model.task_damage(task_100) * 3
        )

    def test_zero_reps(self):
        task = Task(name="none", params={"omni": 5, "reps": 0})
        assert self.model.task_damage(task) == 0.0


class TestDUETProbability:
    def setup_method(self):
        self.model = DUET()

    def test_zero_damage(self):
        assert self.model.probability(0) == 0.0

    def test_output_is_between_0_and_1(self):
        for cd in [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0]:
            p = self.model.probability(cd)
            assert 0 < p < 1, f"probability({cd}) = {p}"

    def test_increases_with_damage(self):
        p_low = self.model.probability(0.001)
        p_high = self.model.probability(1.0)
        assert p_high > p_low

    def test_logistic_formula(self):
        cd = 0.1
        y = 0.766 + 1.515 * math.log10(cd)
        expected = math.exp(y) / (1 + math.exp(y))
        assert self.model.probability(cd) == pytest.approx(expected)


class TestDUETAssessment:
    def setup_method(self):
        self.model = DUET()

    def test_multi_task_pcts_sum_to_100(self):
        tasks = [
            Task(name="a", params={"omni": 3, "reps": 500}),
            Task(name="b", params={"omni": 6, "reps": 200}),
            Task(name="c", params={"omni": 8, "reps": 50}),
        ]
        result = self.model.assess(tasks)
        total_pct = sum(t.pct_total for t in result.tasks)
        assert total_pct == pytest.approx(100.0)

    def test_higher_omni_dominates_damage(self):
        """A few hard exertions should contribute more damage than many easy ones."""
        tasks = [
            Task(name="easy", params={"omni": 2, "reps": 1000}),
            Task(name="hard", params={"omni": 8, "reps": 50}),
        ]
        result = self.model.assess(tasks)
        easy_dmg = result.tasks[0].damage
        hard_dmg = result.tasks[1].damage
        assert hard_dmg > easy_dmg


# ---------------------------------------------------------------------------
# Shoulder Tool unit tests
# ---------------------------------------------------------------------------


class TestShoulderMoment:
    def setup_method(self):
        self.model = ShoulderTool()

    def test_handling_includes_arm_weight(self):
        """Handling moment = load*dist + arm_weight*dist/2."""
        moment = self.model.shoulder_moment(
            load_lb=5, distance_in=18, task_type="handling"
        )
        expected = 5 * 18 + 8.6 * 18 / 2
        assert moment == pytest.approx(expected)

    def test_push_pull_excludes_arm_weight(self):
        moment = self.model.shoulder_moment(
            load_lb=10, distance_in=12, task_type="push_pull"
        )
        assert moment == pytest.approx(10 * 12)

    def test_push_down_excludes_arm_weight(self):
        moment = self.model.shoulder_moment(
            load_lb=10, distance_in=12, task_type="push_down"
        )
        assert moment == pytest.approx(10 * 12)

    def test_zero_load_handling_still_has_arm_weight(self):
        moment = self.model.shoulder_moment(
            load_lb=0, distance_in=18, task_type="handling"
        )
        assert moment > 0  # Arm weight alone contributes

    def test_zero_distance(self):
        moment = self.model.shoulder_moment(
            load_lb=10, distance_in=0, task_type="handling"
        )
        assert moment == 0.0


class TestShoulderPublishedExamples:
    """Verify against published test cases from Bani Hani dissertation."""

    def setup_method(self):
        self.model = ShoulderTool()

    def test_mono_task_2lb_16in_2880reps(self):
        """Published: 2 lb, 16 in, 2880 reps -> CD~0.00428, P~20.8%."""
        tasks = [
            Task(
                name="test",
                params={
                    "load_lb": 2,
                    "distance_in": 16,
                    "reps": 2880,
                },
            )
        ]
        result = self.model.assess(tasks)
        assert result.cumulative_damage == pytest.approx(0.00428, rel=0.15)
        assert result.probability * 100 == pytest.approx(20.8, abs=3.0)


class TestShoulderDamagePerCycle:
    def setup_method(self):
        self.model = ShoulderTool()

    def test_uses_tendon_sn_curve(self):
        """DPC should match tendon_dpc for the same stress level."""
        moment = 5 * 18 + 8.6 * 18 / 2  # handling: 5 lb at 18 in
        stress_pct = (moment / 681) * 100
        expected_dpc = tendon_dpc(stress_pct)
        actual_dpc = self.model.damage_per_cycle(load_lb=5, distance_in=18)
        assert actual_dpc == pytest.approx(expected_dpc)

    def test_damage_increases_with_load(self):
        dpc_light = self.model.damage_per_cycle(load_lb=2, distance_in=16)
        dpc_heavy = self.model.damage_per_cycle(load_lb=10, distance_in=16)
        assert dpc_heavy > dpc_light

    def test_damage_increases_with_distance(self):
        dpc_close = self.model.damage_per_cycle(load_lb=5, distance_in=10)
        dpc_far = self.model.damage_per_cycle(load_lb=5, distance_in=24)
        assert dpc_far > dpc_close


class TestShoulderTaskDamage:
    def setup_method(self):
        self.model = ShoulderTool()

    def test_scales_with_reps(self):
        task_100 = Task(name="a", params={"load_lb": 5, "distance_in": 18, "reps": 100})
        task_400 = Task(name="b", params={"load_lb": 5, "distance_in": 18, "reps": 400})
        assert self.model.task_damage(task_400) == pytest.approx(
            self.model.task_damage(task_100) * 4
        )

    def test_zero_reps(self):
        task = Task(name="none", params={"load_lb": 5, "distance_in": 18, "reps": 0})
        assert self.model.task_damage(task) == 0.0

    def test_default_task_type_is_handling(self):
        task_default = Task(
            name="a", params={"load_lb": 5, "distance_in": 18, "reps": 100}
        )
        task_handling = Task(
            name="b",
            params={
                "load_lb": 5,
                "distance_in": 18,
                "reps": 100,
                "task_type": "handling",
            },
        )
        assert self.model.task_damage(task_default) == self.model.task_damage(
            task_handling
        )


class TestShoulderProbability:
    def setup_method(self):
        self.model = ShoulderTool()

    def test_zero_damage(self):
        assert self.model.probability(0) == 0.0

    def test_output_is_between_0_and_1(self):
        for cd in [0.0001, 0.001, 0.01, 0.1, 1.0, 10.0]:
            p = self.model.probability(cd)
            assert 0 < p < 1, f"probability({cd}) = {p}"

    def test_increases_with_damage(self):
        p_low = self.model.probability(0.001)
        p_high = self.model.probability(1.0)
        assert p_high > p_low

    def test_logistic_formula(self):
        cd = 0.05
        y = 0.870 + 0.932 * math.log10(cd)
        expected = math.exp(y) / (1 + math.exp(y))
        assert self.model.probability(cd) == pytest.approx(expected)


class TestShoulderAssessment:
    def setup_method(self):
        self.model = ShoulderTool()

    def test_multi_task_pcts_sum_to_100(self):
        tasks = [
            Task(name="a", params={"load_lb": 2, "distance_in": 16, "reps": 500}),
            Task(name="b", params={"load_lb": 5, "distance_in": 18, "reps": 200}),
            Task(name="c", params={"load_lb": 10, "distance_in": 20, "reps": 100}),
        ]
        result = self.model.assess(tasks)
        total_pct = sum(t.pct_total for t in result.tasks)
        assert total_pct == pytest.approx(100.0)

    def test_cumulative_damage_is_sum_of_tasks(self):
        tasks = [
            Task(name="a", params={"load_lb": 2, "distance_in": 16, "reps": 500}),
            Task(name="b", params={"load_lb": 5, "distance_in": 18, "reps": 200}),
        ]
        result = self.model.assess(tasks)
        expected_cd = sum(t.damage for t in result.tasks)
        assert result.cumulative_damage == pytest.approx(expected_cd)


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------


class TestModelRegistry:
    def test_get_lifft(self):
        model = get_model("lifft")
        assert isinstance(model, LiFFT)

    def test_get_duet(self):
        model = get_model("duet")
        assert isinstance(model, DUET)

    def test_get_shoulder(self):
        model = get_model("shoulder")
        assert isinstance(model, ShoulderTool)

    def test_case_insensitive(self):
        assert isinstance(get_model("LiFFT"), LiFFT)
        assert isinstance(get_model("DUET"), DUET)
        assert isinstance(get_model("Shoulder"), ShoulderTool)

    def test_unknown_model(self):
        with pytest.raises(ValueError, match="Unknown model"):
            get_model("nonexistent")

    def test_all_models_registered(self):
        assert len(MODELS) == 3


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCLI:
    def run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-m", "fatiguelab.cli", *args],
            capture_output=True,
            text=True,
        )
        return result

    def test_list_shows_all_models(self):
        result = self.run_cli("--list")
        assert result.returncode == 0
        assert "lifft" in result.stdout
        assert "duet" in result.stdout
        assert "shoulder" in result.stdout

    def test_no_args_shows_help(self):
        result = self.run_cli()
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "Examples" in result.stdout

    # LiFFT CLI
    def test_lifft_single_task(self):
        result = self.run_cli("lifft", "--task", "10,0.4,500")
        assert result.returncode == 0
        assert "LiFFT" in result.stdout
        assert "Cumulative Damage" in result.stdout

    def test_lifft_multi_task(self):
        result = self.run_cli("lifft", "-t", "10,0.4,500,A", "-t", "5,0.3,200,B")
        assert result.returncode == 0
        assert "A" in result.stdout
        assert "B" in result.stdout

    def test_lifft_no_tasks_fails(self):
        result = self.run_cli("lifft")
        assert result.returncode != 0

    def test_lifft_bad_task_spec_fails(self):
        result = self.run_cli("lifft", "--task", "10,0.4")
        assert result.returncode != 0

    # DUET CLI
    def test_duet_single_task(self):
        result = self.run_cli("duet", "--task", "4,1350")
        assert result.returncode == 0
        assert "DUET" in result.stdout
        assert "Cumulative Damage" in result.stdout

    def test_duet_multi_task(self):
        result = self.run_cli("duet", "-t", "4,1350,Gripping", "-t", "6,500,Twisting")
        assert result.returncode == 0
        assert "Gripping" in result.stdout
        assert "Twisting" in result.stdout

    def test_duet_no_tasks_fails(self):
        result = self.run_cli("duet")
        assert result.returncode != 0

    def test_duet_bad_task_spec_fails(self):
        result = self.run_cli("duet", "--task", "4")
        assert result.returncode != 0

    # Shoulder CLI
    def test_shoulder_single_task(self):
        result = self.run_cli("shoulder", "--task", "2,16,2880")
        assert result.returncode == 0
        assert "Shoulder" in result.stdout
        assert "Cumulative Damage" in result.stdout

    def test_shoulder_multi_task(self):
        result = self.run_cli(
            "shoulder", "-t", "2,16,2880,Reaching", "-t", "5,18,500,Lifting"
        )
        assert result.returncode == 0
        assert "Reaching" in result.stdout
        assert "Lifting" in result.stdout

    def test_shoulder_with_task_type(self):
        """Push/pull excludes arm weight, so damage should differ from handling."""
        handling = self.run_cli("shoulder", "--task", "10,12,500")
        push_pull = self.run_cli(
            "shoulder", "--task-type", "push_pull", "--task", "10,12,500"
        )
        assert handling.returncode == 0
        assert push_pull.returncode == 0
        assert handling.stdout != push_pull.stdout

    def test_shoulder_no_tasks_fails(self):
        result = self.run_cli("shoulder")
        assert result.returncode != 0

    def test_shoulder_bad_task_spec_fails(self):
        result = self.run_cli("shoulder", "--task", "2,16")
        assert result.returncode != 0
