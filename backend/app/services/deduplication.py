from difflib import SequenceMatcher


def annotate_duplicates(incidents: list[dict]) -> list[dict]:
    # Cache normalized text and location to avoid repeated work.
    seen_by_location: dict[str, list[dict]] = {}

    for item in incidents:
        item["duplicate_of"] = None
        item["conflict_flag"] = False
        item["evidence_status"] = "unverified"

        location = item["location_name"].lower()
        normalized = " ".join(item["text"].lower().split())
        incident_type = item["incident_type"]

        # Only compare reports from the same location.
        prior_reports = seen_by_location.setdefault(location, [])

        for prior in prior_reports:
            similar = (
                SequenceMatcher(
                    None, normalized, prior["_normalized_text"]
                ).ratio() >= 0.82
            )

            if similar:
                item["duplicate_of"] = prior["incident_id"]
                item["evidence_status"] = "corroborated"
                break

            if (
                incident_type != prior["incident_type"]
                and incident_type != "general_emergency"
            ):
                item["conflict_flag"] = True
                item["evidence_status"] = "conflicting"

        # Store cached data separately from the public incident fields.
        prior_reports.append({
            "incident_id": item["incident_id"],
            "incident_type": incident_type,
            "_normalized_text": normalized,
        })

    return incidents
