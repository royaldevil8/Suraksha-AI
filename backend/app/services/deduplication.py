from difflib import SequenceMatcher

DUPLICATE_THRESHOLD = 0.82
POTENTIAL_CONFLICT_THRESHOLD = 0.65


def annotate_duplicates(incidents: list[dict]) -> list[dict]:
    seen_by_location: dict[str, list[dict]] = {}

    for item in incidents:
        item["duplicate_of"] = None
        item["conflict_flag"] = False
        item["evidence_status"] = "unverified"

        location = str(item.get("location_name") or "unknown").strip().lower()
        normalized = " ".join(str(item.get("text", "")).lower().split())
        incident_type = item.get("incident_type", "general_emergency")
        prior_reports = seen_by_location.setdefault(location, [])

        for prior in prior_reports:
            prior_text = prior["_normalized_text"]

            # Exact match is the fastest duplicate case.
            if normalized == prior_text:
                item["duplicate_of"] = prior["incident_id"]
                break

            # A cheap upper bound avoids expensive ratio() calls when
            # the strings cannot possibly reach either threshold.
            matcher = SequenceMatcher(None, normalized, prior_text)

            duplicate_possible = matcher.quick_ratio() >= DUPLICATE_THRESHOLD
            conflict_possible = (
                incident_type != prior["incident_type"]
                and incident_type != "general_emergency"
                and prior["incident_type"] != "general_emergency"
                and matcher.quick_ratio() >= POTENTIAL_CONFLICT_THRESHOLD
            )

            if not duplicate_possible and not conflict_possible:
                continue

            similarity = matcher.ratio()

            if (
                conflict_possible
                and similarity >= POTENTIAL_CONFLICT_THRESHOLD
            ):
                item["conflict_flag"] = True

            if similarity >= DUPLICATE_THRESHOLD:
                item["duplicate_of"] = prior["incident_id"]
                break

        if item["conflict_flag"]:
            item["evidence_status"] = "conflicting"
        elif item["duplicate_of"]:
            item["evidence_status"] = "corroborated"

        prior_reports.append({
            "incident_id": item["incident_id"],
            "incident_type": incident_type,
            "_normalized_text": normalized,
        })

    return incidents
