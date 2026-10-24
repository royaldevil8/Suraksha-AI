from app.services.extraction import extract_report

class IncidentAgent:
    name = "incident_analysis"
    def run(self, report: dict) -> dict:
        return {"agent": self.name, "output": extract_report(report)}
