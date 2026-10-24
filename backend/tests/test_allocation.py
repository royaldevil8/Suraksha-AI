from app.services.allocation import allocate_resources


def make_incident(
    incident_id,
    risk_score,
    urgency=3,
    resources_needed=None,
    duplicate_of=None,
):
    return {
        "incident_id": incident_id,
        "risk_score": risk_score,
        "urgency": urgency,
        "resources_needed": resources_needed or [],
        "duplicate_of": duplicate_of,
        "assigned_resources": [],
    }


def test_duplicate_incident_gets_no_resources():
    incidents = [
        make_incident("INC-1", 90, resources_needed=["ambulance"]),
        make_incident(
            "INC-2", 80,
            resources_needed=["ambulance"],
            duplicate_of="INC-1",
        ),
    ]

    result, remaining = allocate_resources(incidents)

    duplicate = next(i for i in result if i["incident_id"] == "INC-2")
    assert duplicate["assigned_resources"] == []


def test_allocation_never_exceeds_inventory():
    incidents = [
        make_incident(
            f"INC-{n}", 100 - n,
            resources_needed=["ambulance", "boat", "medical_kit"],
        )
        for n in range(30)
    ]

    result, remaining = allocate_resources(incidents)

    assert all(item["available"] >= 0 for item in remaining)

    for item in remaining:
        original = {
            "ambulance": 3,
            "rescue_team": 4,
            "boat": 2,
            "medical_kit": 20,
            "shelter_space": 100,
        }[item["type"]]
        assert item["available"] <= original

    assert len(result) == 30


def test_higher_risk_incident_gets_first_available_resource():
    incidents = [
        make_incident("LOW", 20, urgency=2, resources_needed=["ambulance"]),
        make_incident("HIGH", 90, urgency=5, resources_needed=["ambulance"]),
    ]

    result, remaining = allocate_resources(incidents)

    by_id = {item["incident_id"]: item for item in result}
    assert by_id["HIGH"]["assigned_resources"] == ["ambulance"]
    assert by_id["LOW"]["assigned_resources"] == ["ambulance"]
    assert next(r for r in remaining if r["type"] == "ambulance")["available"] == 1


def test_unknown_resource_type_does_not_change_inventory():
    incidents = [
        make_incident("INC-X", 70, resources_needed=["unknown_resource"])
    ]

    result, remaining = allocate_resources(incidents)

    assert result[0]["assigned_resources"] == []
    assert {r["type"]: r["available"] for r in remaining} == {
        "ambulance": 3,
        "rescue_team": 4,
        "boat": 2,
        "medical_kit": 20,
        "shelter_space": 100,
    }
def test_conflicting_incident_gets_no_automatic_resources():
    incidents = [
        {
            **make_incident(
                "INC-CONFLICT",
                95,
                urgency=5,
                resources_needed=["ambulance"],
            ),
            "conflict_flag": True,
        }
    ]

    result, remaining = allocate_resources(incidents)

    assert result[0]["assigned_resources"] == []
    assert next(
        r for r in remaining if r["type"] == "ambulance"
    )["available"] == 3
