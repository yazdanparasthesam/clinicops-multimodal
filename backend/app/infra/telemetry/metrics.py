"""Business metrics for ClinicOps — Prometheus counters for golden-journey dashboard.

ClinicOps-native naming (no fs_* reuse). Tested by tests/unit/test_telemetry.py.
"""
from prometheus_client import Counter, Histogram

# Primary ClinicOps counters
clinicops_statements = Counter(
    "clinicops_statements_generated_total",
    "Statements/visits generated",
    ["kind"],
)
clinicops_validations = Counter(
    "clinicops_validation_runs_total",
    "Validation runs",
    ["outcome"],
)
clinicops_transitions = Counter(
    "clinicops_workflow_transitions_total",
    "Workflow transitions",
    ["action", "to_status"],
)
clinicops_ai_requests = Counter(
    "clinicops_ai_requests_total",
    "AI requests",
    ["kind", "provider", "status"],
)
clinicops_ai_duration = Histogram(
    "clinicops_ai_request_duration_seconds",
    "AI request duration",
    ["kind"],
)
clinicops_journey = Histogram(
    "clinicops_journey_step_duration_seconds",
    "Journey step duration",
    ["step"],
)

_METRIC_NAMES = [
    "clinicops_statements_generated_total",
    "clinicops_validation_runs_total",
    "clinicops_workflow_transitions_total",
    "clinicops_ai_requests_total",
    "clinicops_ai_request_duration_seconds",
    "clinicops_journey_step_duration_seconds",
]

def register_metrics():
    return list(_METRIC_NAMES)

def inc_statement(kind: str = "visit"):
    clinicops_statements.labels(kind=kind).inc()

def inc_validation(failures: int = 0):
    outcome = "passed" if failures == 0 else "failed"
    clinicops_validations.labels(outcome=outcome).inc()

def inc_transition(action: str, to_status: str):
    clinicops_transitions.labels(action=action, to_status=to_status).inc()

def observe_ai_call(kind: str, provider: str, status: str, duration_s: float):
    clinicops_ai_requests.labels(kind=kind, provider=provider, status=status).inc()
    clinicops_ai_duration.labels(kind=kind).observe(duration_s)

def observe_journey_step(step: str, duration_s: float):
    clinicops_journey.labels(step=step).observe(duration_s)
