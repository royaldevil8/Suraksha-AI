
import re
from difflib import SequenceMatcher

DUPLICATE_THRESHOLD = 0.82
POTENTIAL_CONFLICT_THRESHOLD = 0.65


def _affected_count(text: str) -> int | None:
    pattern = (
        r"\b(\d+)\s+(?:people|persons|individuals)\s+"
        r"(?:are\s+)?(?:trapped|injured|affected)\b"
    )

    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def annotate_duplicates(incidents: list[dict]) -> list[dict]:
    seen_by_location: dict[str, list[dict]] = {}

    for item in incidents:
        item["duplicate_of"] = None
        item["conflict_flag"] = False
        item["evidence_status"] = "unverified"

        location = str(
            item.get("location_name") or "unknown"
        ).strip().lower()

        normalized = " ".join(
            str(item.get("text", "")).lower().split()
        )

        incident_type = item.get(
            "incident_type", "general_emergency"
        )
        current_count = _affected_count(normalized)
        prior_reports = seen_by_location.setdefault(location, [])

        count_mismatch_found = False
        type_conflict_found = False
        matching_duplicate = None

        for prior in prior_reports:
            prior_count = prior["_affected_count"]
            prior_text = prior["_normalized_text"]

            # Different explicit counts must not be merged.
            if (
                current_count is not None
                and prior_count is not None
                and current_count != prior_count
            ):
                count_mismatch_found = True
                continue

            
            matcher = SequenceMatcher(None, normalized, prior_text)
            similarity = matcher.ratio()

            # Different specific incident types require review.
            types_differ = (
                incident_type != prior["incident_type"]
                and incident_type != "general_emergency"
                and prior["incident_type"] != "general_emergency"
            )

            if types_differ:
                type_conflict_found = True
                continue

            # Only matching types and sufficiently similar text
            # can be linked as duplicates.
            if similarity >= DUPLICATE_THRESHOLD:
                matching_duplicate = prior["incident_id"]
                break


        # A valid duplicate match takes precedence over an unrelated
        # count mismatch in another report at the same location.
        if matching_duplicate is not None:
            item["duplicate_of"] = matching_duplicate
        else:
            item["conflict_flag"] = (
                count_mismatch_found or type_conflict_found
            )

        item["evidence_status"] = (
            "conflicting"
            if item["conflict_flag"]
            else "unverified"
        )

        prior_reports.append({
            "incident_id": item["incident_id"],
            "incident_type": incident_type,
            "_normalized_text": normalized,
            "_affected_count": current_count,
        })

    return incidents
