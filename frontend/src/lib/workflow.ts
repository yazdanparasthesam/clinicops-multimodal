export const STATES = ["draft","submitted","in_review","approved","dispensed","changes_requested","rejected"] as const
export type VisitStatus = typeof STATES[number]

export function nextActions(status: string, role: string): string[] {
  if (status === "draft" && (role === "nurse" || role === "doctor")) return ["submit"]
  if (status === "submitted" && role === "doctor") return ["start_review"]
  if (status === "in_review" && role === "doctor") return ["approve","request_changes","reject"]
  if (status === "approved" && role === "pharmacist") return ["dispense"]
  if (status === "changes_requested") return ["reopen"]
  return []
}

export const ACTION_LABELS: Record<string,string> = {
  submit: "Submit",
  reopen: "Reopen",
  start_review: "Start Review",
  request_changes: "Request Changes",
  reject: "Reject",
  approve: "Approve",
  dispense: "Dispense",
}

export const STATUS_META: Record<string, { label: string; badge: string; desc: string }> = {
  draft: { label: "Draft", badge: "bg-gray-100", desc: "Draft visit — intake incomplete, ready to submit" },
  submitted: { label: "Submitted", badge: "bg-blue-100", desc: "Submitted for review by doctor" },
  in_review: { label: "In Review", badge: "bg-amber-100", desc: "Under review by doctor — validations and AI drafts checked" },
  changes_requested: { label: "Changes Requested", badge: "bg-orange-100", desc: "Doctor requested changes — edit intake and resubmit" },
  approved: { label: "Approved", badge: "bg-green-100", desc: "Approved by doctor — ready for dispensing" },
  dispensed: { label: "Dispensed", badge: "bg-green-200", desc: "Dispensed by pharmacist — workflow complete" },
  rejected: { label: "Rejected", badge: "bg-red-100", desc: "Rejected after review — visit closed" },
}

export function nextActionsCompat(status: string, role: string): string[] {
  return nextActions(status, role)
}
