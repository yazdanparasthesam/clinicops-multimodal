"""Business metrics for ClinicOps — Prometheus counters compatible with
Financial-Statement golden-journey dashboard (fs_* names).

Keeps Grafana dashboard metric names stable while ClinicOps adds alias
clinicops_* for future rename. Tested by tests/unit/test_telemetry.py.
"""
from prometheus_client import Counter, Histogram, REGISTRY

# Core business counters (Financial-Statement names for dashboard compatibility)
_fs_statements = Counter(
    "fs_statements_generated_total",
    "Statements/visits generated",
    ["kind"],
)
_fs_validations = Counter(
    "fs_validation_runs_total",
    "Validation runs",
    ["outcome"],
)
_fs_transitions = Counter(
    "fs_workflow_transitions_total",
    "Workflow transitions",
    ["action", "to_status"],
)
_fs_ai_requests = Counter(
    "fs_ai_requests_total",
    "AI requests",
    ["kind", "provider", "status"],
)
_fs_ai_duration = Histogram(
    "fs_ai_request_duration_seconds",
    "AI request duration",
    ["kind"],
)
_fs_journey = Histogram(
    "fs_journey_step_duration_seconds",
    "Journey step duration",
    ["step"],
)

# ClinicOps aliases (same underlying series, optional future use)
clinicops_visits = Counter("clinicops_visits_total", "Visits created", ["kind"])
clinicops_validations = Counter("clinicops_validations_total", "Validations", ["outcome"])

_METRIC_NAMES = [
    "fs_statements_generated_total",
    "fs_validation_runs_total",
    "fs_workflow_transitions_total",
    "fs_ai_requests_total",
    "fs_ai_request_duration_seconds",
    "fs_journey_step_duration_seconds",
]

def register_metrics():
    """Return documented metric names — used by tests and dashboard discovery."""
    # Ensure metrics are registered (already created at import)
    return list(_METRIC_NAMES)

def inc_statement(kind: str = "visit"):
    _fs_statements.labels(kind=kind).inc()
    # alias
    try:
        clinicops_visits.labels(kind=kind).inc()
    except Exception:
        pass

def inc_validation(failures: int = 0):
    outcome = "passed" if failures == 0 else "failed"
    _fs_validations.labels(outcome=outcome).inc()
    try:
        clinicops_validations.labels(outcome=outcome).inc()
    except Exception:
        pass

def inc_transition(action: str, to_status: str):
    _fs_transitions.labels(action=action, to_status=to_status).inc()

def observe_ai_call(kind: str, provider: str, status: str, duration_s: float):
    _fs_ai_requests.labels(kind=kind, provider=provider, status=status).inc()
    _fs_ai_duration.labels(kind=kind).observe(duration_s)

def observe_journey_step(step: str, duration_s: float):
    _fs_journey.labels(step=step).observe(duration_s)
