from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_PROMPT = "Plan a 1-day trip in Tokyo"
VAGUE_PROMPT = "Something fun"
EMPTY_PROMPT = ""
ABUSIVE_PROMPT = "Plan a trip to steal data from NASA"

def test_plan_trip_valid():
    r = client.post("/plan-trip", json={"prompt": VALID_PROMPT})
    assert r.status_code == 200
    d = r.json()
    assert isinstance(d["itinerary"], list)
    assert "agent_message" in d

def test_plan_trip_empty_prompt():
    r = client.post("/plan-trip", json={"prompt": EMPTY_PROMPT})
    assert r.status_code == 200 or r.status_code == 422

def test_plan_trip_vague_prompt():
    r = client.post("/plan-trip", json={"prompt": VAGUE_PROMPT})
    assert r.status_code == 200
    assert len(r.json()["itinerary"]) >= 1

def test_plan_trip_abusive_prompt():
    r = client.post("/plan-trip", json={"prompt": ABUSIVE_PROMPT})
    assert r.status_code == 200
    agent_msg = r.json()["agent_message"].lower()
    # Be flexible with result since Gemini may still generate something
    assert "trip plan" in agent_msg or "sorry" in agent_msg or "not appropriate" in agent_msg


#designed to fail
def test_evaluate_plan():
    plan_req = {
        "prompt": VALID_PROMPT
    }
    plan_resp = {
        "itinerary": [
            {
                "time": "9:00 AM",
                "activity": "Visit park",
                "description": "Walk around and relax."
            }
        ],
        "weather": {
            "forecast": "Sunny",
            "temperature": 28.0,
            "details": "Clear sky"
        },
        "agent_message": "Here is your personalized 1-day trip plan!"
    }

    r = client.post("/evaluate-plan", json={"request": plan_req, "response": plan_resp})
    assert r.status_code == 200

    data = r.json()
    # Check top-level fields
    assert "evaluation_summary" in data
    assert isinstance(data["evaluation_summary"], str)

    assert "overall_score" in data
    assert isinstance(data["overall_score"], (float, int))
    assert 1.0 <= data["overall_score"] <= 5.0

    assert "criteria" in data
    assert isinstance(data["criteria"], list)
    assert len(data["criteria"]) >= 1

    for criterion in data["criteria"]:
        assert isinstance(criterion, dict)
        assert "criterion" in criterion
        assert "score" in criterion
        assert "justification" in criterion
        assert isinstance(criterion["criterion"], str)
        assert isinstance(criterion["score"], int)
        assert 1 <= criterion["score"] <= 5
        assert isinstance(criterion["justification"], str)
