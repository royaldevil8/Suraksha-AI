from app.services.risk_scoring import score_incident


def make_incident(**overrides):
    incident = {
        "urgency": 5,
        "estimated_affected": 100,
        "confidence": 1.0,
        "text": "Flood emergency",
        "conflict_flag": False,
        "duplicate_of": None,
    }
    incident.update(overrides)
    return incident


def test_high_severity_incident_gets_critical_priority():
    incident = score_incident(make_incident())

    assert incident["risk_score"] == 80
    assert incident["priority"] == "CRITICAL"
    assert incident["explanation"]


def test_conflict_reduces_risk_score():
    normal = score_incident(make_incident())
    conflicting = score_incident(make_incident(conflict_flag=True))

    assert conflicting["risk_score"] == normal["risk_score"] - 8
    assert any("Conflicting" in reason for reason in conflicting["explanation"])


def test_duplicate_reduces_risk_score():
    normal = score_incident(make_incident())
    duplicate = score_incident(make_incident(duplicate_of="INC-ORIGINAL"))

    assert duplicate["risk_score"] == normal["risk_score"] - 12
    assert any("duplicate" in reason.lower() for reason in duplicate["explanation"])


def test_vulnerability_increases_score_and_explains_why():
    normal = score_incident(make_incident())
    vulnerable = score_incident(make_incident(text="Children trapped in flood"))

    assert vulnerable["risk_score"] == normal["risk_score"] + 10
    assert any("vulnerable" in reason.lower() for reason in vulnerable["explanation"])


def test_low_confidence_adds_verification_warning():
    incident = score_incident(make_incident(confidence=0.4))

    assert any("verification" in reason.lower() for reason in incident["explanation"])


def test_score_stays_within_zero_and_hundred():
    incident = score_incident(make_incident(
        urgency=5,
        estimated_affected=1000,
        confidence=1.0,
        text="Children trapped in hospital",
    ))

    assert 0 <= incident["risk_score"] <= 100
