from app.services.risk_scoring import score_incident

class RiskAgent:
    name = "risk_assessment"
    def run(self, incident: dict) -> dict:
        return {"agent": self.name, "output": score_incident(incident)}
