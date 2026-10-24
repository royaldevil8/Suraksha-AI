from app.services.allocation import allocate_resources

class LogisticsAgent:
    name = "logistics_planning"
    def run(self, incidents: list[dict]) -> dict:
        assigned, remaining = allocate_resources(incidents)
        return {"agent": self.name, "output": {"incidents": assigned, "remaining_resources": remaining}}
