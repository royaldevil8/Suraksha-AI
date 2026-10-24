
from app.services.deduplication import annotate_duplicates


def make_incident(incident_id, text, location="Rampur", incident_type="flood"):
    return {
        "incident_id": incident_id,
        "text": text,
        "location_name": location,
        "incident_type": incident_type,
    }


def test_identical_reports_at_same_location_are_duplicates():
    incidents = [
        make_incident("A", "Flood water rising fast near Rampur"),
        make_incident("B", "Flood water rising fast near Rampur"),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["duplicate_of"] == "A"
    assert result[1]["evidence_status"] == "unverified"


def test_reports_at_different_locations_are_not_duplicates():
    incidents = [
        make_incident("A", "Flood water rising fast", "Rampur"),
        make_incident("B", "Flood water rising fast", "Shivpur"),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["duplicate_of"] is None


def test_conflicting_incident_types_are_flagged():
    incidents = [
        make_incident("A", "Fire reported in the area", incident_type="fire"),
        make_incident("B", "Flood reported in the area", incident_type="flood"),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["conflict_flag"] is True
    assert result[1]["evidence_status"] == "conflicting"


def test_first_report_remains_unverified():
    incidents = [
        make_incident("A", "Flood water rising near Rampur"),
    ]
    result = annotate_duplicates(incidents)
    assert result[0]["duplicate_of"] is None
    assert result[0]["evidence_status"] == "unverified"


def test_same_location_but_different_incidents_are_not_duplicates():
    incidents = [
        make_incident("A", "Flood water rising near the north bridge"),
        make_incident("B", "Flood water rising near the south hospital"),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["duplicate_of"] is None


def test_same_text_different_locations_remain_separate():
    incidents = [
        make_incident("A", "Flood water rising fast", "Rampur"),
        make_incident("B", "Flood water rising fast", "Shivpur"),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["duplicate_of"] is None


def test_repeated_report_does_not_prove_independent_corroboration():
    incidents = [
        make_incident("A", "Flood water rising fast near Rampur"),
        make_incident("B", "Flood water rising fast near Rampur"),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["duplicate_of"] == "A"
    assert result[1]["evidence_status"] == "unverified"


def test_different_affected_counts_are_not_automatically_duplicates():
    incidents = [
        make_incident(
            "A",
            "Flood water rising fast near Sector 4; "
            "2 people trapped, urgent boat and rescue support needed.",
            location="Sector 4",
        ),
        make_incident(
            "B",
            "Flood water rising fast near Sector 4; "
            "40 people trapped, urgent boat and rescue support needed.",
            location="Sector 4",
        ),
    ]
    result = annotate_duplicates(incidents)
    assert result[1]["duplicate_of"] is None

def test_matching_duplicate_is_not_conflicting_due_to_unrelated_count():
    incidents = [
        make_incident(
            "A",
            "Flood near Sector 4; 2 people trapped.",
            location="Sector 4",
        ),
        make_incident(
            "B",
            "Flood near Sector 4; 40 people trapped.",
            location="Sector 4",
        ),
        make_incident(
            "C",
            "Flood near Sector 4; 40 people trapped.",
            location="Sector 4",
        ),
    ]

    result = annotate_duplicates(incidents)

    assert result[1]["duplicate_of"] is None
    assert result[2]["duplicate_of"] == "B"
    assert result[2]["conflict_flag"] is False
    assert result[2]["evidence_status"] == "unverified"
