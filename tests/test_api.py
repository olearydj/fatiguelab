"""Tests for the web API."""

import pytest
from fastapi.testclient import TestClient

from fatiguelab.api import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/models
# ---------------------------------------------------------------------------


class TestModelsEndpoint:
    def test_returns_all_models(self):
        r = client.get("/api/models")
        assert r.status_code == 200
        models = r.json()["models"]
        ids = [m["id"] for m in models]
        assert "lifft" in ids
        assert "duet" in ids
        assert "shoulder" in ids

    def test_model_has_required_keys(self):
        r = client.get("/api/models")
        for model in r.json()["models"]:
            assert "id" in model
            assert "name" in model
            assert "description" in model
            assert "fields" in model
            assert len(model["fields"]) > 0

    def test_fields_have_required_keys(self):
        r = client.get("/api/models")
        for model in r.json()["models"]:
            for field in model["fields"]:
                assert "name" in field
                assert "label" in field
                assert "type" in field

    def test_duet_has_omni_select(self):
        r = client.get("/api/models")
        duet = next(m for m in r.json()["models"] if m["id"] == "duet")
        omni_field = next(f for f in duet["fields"] if f["name"] == "omni")
        assert omni_field["type"] == "select"
        assert len(omni_field["options"]) == 11  # 0 through 10

    def test_shoulder_has_task_type_select(self):
        r = client.get("/api/models")
        shoulder = next(m for m in r.json()["models"] if m["id"] == "shoulder")
        tt_field = next(f for f in shoulder["fields"] if f["name"] == "task_type")
        assert tt_field["type"] == "select"
        values = [o["value"] for o in tt_field["options"]]
        assert "handling" in values
        assert "push_pull" in values
        assert "push_down" in values


# ---------------------------------------------------------------------------
# POST /api/assess - LiFFT
# ---------------------------------------------------------------------------


class TestAssessLiFFT:
    def test_single_task(self):
        r = client.post(
            "/api/assess",
            json={
                "model": "lifft",
                "tasks": [
                    {
                        "name": "Lift",
                        "params": {"load_kg": 10, "distance_m": 0.4, "reps": 500},
                    }
                ],
            },
        )
        assert r.status_code == 200
        d = r.json()
        assert d["model"] == "LiFFT"
        assert d["cumulative_damage"] > 0
        assert 0 < d["probability"] < 1
        assert len(d["tasks"]) == 1
        assert d["tasks"][0]["pct_total"] == pytest.approx(100.0)

    def test_multi_task(self):
        r = client.post(
            "/api/assess",
            json={
                "model": "lifft",
                "tasks": [
                    {
                        "name": "A",
                        "params": {"load_kg": 15, "distance_m": 0.45, "reps": 600},
                    },
                    {
                        "name": "B",
                        "params": {"load_kg": 5, "distance_m": 0.3, "reps": 300},
                    },
                ],
            },
        )
        assert r.status_code == 200
        d = r.json()
        assert len(d["tasks"]) == 2
        total_pct = sum(t["pct_total"] for t in d["tasks"])
        assert total_pct == pytest.approx(100.0)

    def test_matches_cli_output(self):
        """API should produce same results as the CLI calculator."""
        r = client.post(
            "/api/assess",
            json={
                "model": "lifft",
                "tasks": [
                    {
                        "name": "A",
                        "params": {"load_kg": 10, "distance_m": 0.4, "reps": 500},
                    },
                    {
                        "name": "B",
                        "params": {"load_kg": 5, "distance_m": 0.3, "reps": 200},
                    },
                    {
                        "name": "C",
                        "params": {"load_kg": 20, "distance_m": 0.5, "reps": 100},
                    },
                ],
            },
        )
        d = r.json()
        # Cross-check against known CLI output
        assert d["cumulative_damage"] == pytest.approx(0.004871, rel=0.01)
        assert d["probability"] == pytest.approx(0.340, abs=0.01)


# ---------------------------------------------------------------------------
# POST /api/assess - DUET
# ---------------------------------------------------------------------------


class TestAssessDUET:
    def test_published_example(self):
        """Figure 2: OMNI=2, 5400 reps -> CD=0.0074, P=26.5%."""
        r = client.post(
            "/api/assess",
            json={
                "model": "duet",
                "tasks": [{"name": "Test", "params": {"omni": 2, "reps": 5400}}],
            },
        )
        assert r.status_code == 200
        d = r.json()
        assert d["model"] == "DUET"
        assert d["cumulative_damage"] == pytest.approx(0.0074, rel=0.02)
        assert d["probability"] * 100 == pytest.approx(26.5, abs=0.5)

    def test_multi_task(self):
        r = client.post(
            "/api/assess",
            json={
                "model": "duet",
                "tasks": [
                    {"name": "Easy", "params": {"omni": 3, "reps": 2000}},
                    {"name": "Hard", "params": {"omni": 8, "reps": 150}},
                ],
            },
        )
        assert r.status_code == 200
        d = r.json()
        # Hard task should dominate
        hard_task = next(t for t in d["tasks"] if t["name"] == "Hard")
        easy_task = next(t for t in d["tasks"] if t["name"] == "Easy")
        assert hard_task["damage"] > easy_task["damage"]


# ---------------------------------------------------------------------------
# POST /api/assess - Shoulder
# ---------------------------------------------------------------------------


class TestAssessShoulder:
    def test_published_example(self):
        """2 lb, 16 in, 2880 reps -> CD~0.00428, P~20.8%."""
        r = client.post(
            "/api/assess",
            json={
                "model": "shoulder",
                "tasks": [
                    {
                        "name": "Test",
                        "params": {
                            "load_lb": 2,
                            "distance_in": 16,
                            "reps": 2880,
                        },
                    }
                ],
            },
        )
        assert r.status_code == 200
        d = r.json()
        assert d["model"] == "Shoulder Tool"
        assert d["cumulative_damage"] == pytest.approx(0.00428, rel=0.15)
        assert d["probability"] * 100 == pytest.approx(20.8, abs=3.0)

    def test_task_type_affects_result(self):
        base = {"load_lb": 10, "distance_in": 12, "reps": 500}
        r1 = client.post(
            "/api/assess",
            json={
                "model": "shoulder",
                "tasks": [{"name": "A", "params": {**base, "task_type": "handling"}}],
            },
        )
        r2 = client.post(
            "/api/assess",
            json={
                "model": "shoulder",
                "tasks": [{"name": "A", "params": {**base, "task_type": "push_pull"}}],
            },
        )
        # Handling includes arm weight, so damage should be higher
        assert r1.json()["cumulative_damage"] > r2.json()["cumulative_damage"]


# ---------------------------------------------------------------------------
# POST /api/assess - error cases
# ---------------------------------------------------------------------------


class TestAssessErrors:
    def test_unknown_model(self):
        r = client.post("/api/assess", json={"model": "bogus", "tasks": []})
        assert r.status_code == 400

    def test_missing_params(self):
        r = client.post(
            "/api/assess",
            json={
                "model": "lifft",
                "tasks": [{"name": "bad", "params": {}}],
            },
        )
        assert r.status_code == 400

    def test_empty_tasks_returns_zero(self):
        r = client.post("/api/assess", json={"model": "lifft", "tasks": []})
        assert r.status_code == 200
        d = r.json()
        assert d["cumulative_damage"] == 0
        assert d["probability"] == 0
        assert d["tasks"] == []

    def test_invalid_json(self):
        r = client.post(
            "/api/assess",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------


class TestStaticFiles:
    def test_index_page(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Fatigue Failure Risk Calculator" in r.text

    def test_index_has_model_cards_container(self):
        r = client.get("/")
        assert 'id="model-cards"' in r.text

    def test_index_fetches_models(self):
        r = client.get("/")
        assert "/api/models" in r.text
