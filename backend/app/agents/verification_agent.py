from app.services.deduplication import annotate_duplicates

class VerificationAgent:
    name = "evidence_verification"
    def run(self, incidents: list[dict]) -> dict:
        return {"agent": "evidence_verification", "output": annotate_duplicates(incidents)}
