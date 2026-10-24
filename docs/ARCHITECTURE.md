# SURAKSHA AI — Architecture and implementation decisions

## End-to-end flow
```text
Synthetic / approved reports
        ↓
Ingestion + schema validation
        ↓
Incident extraction agent
        ↓
Deduplication + conflict / evidence checks
        ↓
Risk scoring agent (transparent weighted rules)
        ↓
Logistics agent (resource-constrained greedy baseline)
        ↓
API response + audit-friendly explanation
        ↓
React command dashboard + scenario replay
```

## Agent contracts
- IncidentAgent: raw report → structured incident.
- VerificationAgent: incidents → duplicate/conflict/evidence annotations.
- RiskAgent: incident → score, priority, explanation list.
- LogisticsAgent: prioritized incidents + inventory → assignments + remaining stock.

The current API orchestration uses the same service functions as these thin agent wrappers, so behavior is testable and deterministic. A later iteration can replace a stage behind the same input/output contract.

## Risk score (prototype heuristic)
Score is bounded to 0–100 and built from urgency (0–35), estimated affected population (0–25), evidence confidence (0–20), vulnerability signal (0–10), and penalties for conflicts/duplicates. It is a demonstration score, not a validated disaster triage standard.

## Next development milestones
1. Confirm report schema and improve labeled synthetic data.
2. Add source-aware provenance and evidence links.
3. Add proper incident clustering and location normalization.
4. Replace greedy assignment with OR-Tools or a tested optimizer; include travel-time and capacity constraints.
5. Add map visualization (Leaflet) and incident timeline.
6. Add an optional LLM extraction adapter with schema validation, timeout, fallback and cost/rate-limit controls.
7. Add metrics: extraction field accuracy, duplicate precision/recall, allocation feasibility, latency, and scenario outcomes.
8. Add operator review states, audit events, role permissions and exportable incident brief.

## Critical design rules
- Never convert low confidence into a confirmed fact.
- Keep the score explanation attached to the incident.
- Respect inventory constraints; never allocate negative stock.
- Scenario replay should be reproducible and show what changed.
- Use only synthetic or approved data in the hackathon demo.
