
from app.services.extraction import extract_report


def test_confirmed_fire_is_recognized_as_fire():
    incident = extract_report({
        "report_id": "FIRE-001",
        "text": "Field volunteer reports a confirmed fire at Rampur.",
        "location_name": "Rampur",
        "confidence": 0.9,
    })

    assert incident["incident_type"] == "fire"
    assert incident["urgency"] >= 3
    assert incident["uncertainty_flag"] is False


def test_severe_fire_gets_high_urgency():
    incident = extract_report({
        "report_id": "FIRE-002",
        "text": "Severe fire spreading rapidly, urgent rescue needed at Rampur.",
        "location_name": "Rampur",
        "confidence": 0.9,
    })

    assert incident["incident_type"] == "fire"
    assert incident["urgency"] == 4


def test_unconfirmed_fire_remains_uncertain():
    incident = extract_report({
        "report_id": "FIRE-003",
        "text": "Unconfirmed social post claims a fire at Rampur.",
        "location_name": "Rampur",
        "confidence": 0.9,
    })

    assert incident["incident_type"] == "fire"
    assert incident["uncertainty_flag"] is True
    assert incident["confidence"] == 0.5
