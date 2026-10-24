from time import perf_counter
from app.services.orchestrator import load_reports
from app.services.extraction import extract_report
from app.services.deduplication import annotate_duplicates
from app.services.risk_scoring import score_incident
from app.services.allocation import allocate_resources

t0 = perf_counter()
raw = load_reports()
t1 = perf_counter()

incidents = [extract_report(r) for r in raw]
t2 = perf_counter()

incidents = annotate_duplicates(incidents)
t3 = perf_counter()

incidents = [score_incident(i) for i in incidents]
t4 = perf_counter()

incidents, remaining = allocate_resources(incidents)
t5 = perf_counter()

print(f"Reports loaded: {len(raw)}")
print(f"Load:          {t1-t0:.3f}s")
print(f"Extraction:    {t2-t1:.3f}s")
print(f"Deduplication: {t3-t2:.3f}s")
print(f"Risk scoring:  {t4-t3:.3f}s")
print(f"Allocation:    {t5-t4:.3f}s")
print(f"Total:         {t5-t0:.3f}s")
print(f"Duplicates:    {sum(bool(i['duplicate_of']) for i in incidents)}")
print(f"Conflicts:     {sum(bool(i['conflict_flag']) for i in incidents)}")
