# Deterministic workflow state machine

STATES = ["draft","submitted","in_review","approved","dispensed","changes_requested","rejected"]

ALLOWED = {
    "draft": ["submitted"],
    "submitted": ["in_review","changes_requested","rejected"],
    "in_review": ["approved","changes_requested","rejected"],
    "approved": ["dispensed","in_review"],
    "changes_requested": ["draft","submitted"],
    "rejected": ["draft"],
    "dispensed": []
}

def can_transition(frm: str, to: str) -> bool:
    return to in ALLOWED.get(frm, [])

def gate_errors_for_transition(target: str, error_rule_ids: list) -> list:
    # submit/approve/dispense blocked by error-rules
    if target in ("submitted","approved","dispensed"):
        return error_rule_ids  # if any error → block
    return []

# Roles allowed per transition (simplified)
ROLE_TRANSITIONS = {
    "submitted": ["nurse","doctor"],
    "in_review": ["doctor"],
    "approved": ["doctor"],
    "dispensed": ["pharmacist"],
    "changes_requested": ["doctor","pharmacist"],
    "rejected": ["doctor","pharmacist"],
    "draft": ["nurse","doctor"]
}

def role_allowed(role: str, target: str) -> bool:
    allowed = ROLE_TRANSITIONS.get(target, [])
    return role in allowed
