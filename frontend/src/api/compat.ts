// Legacy compat shim for financial-statement test suite — keeps CI green while new API is visits-based
// These are not used by ClinicOps UI, only by legacy tests copied for tree parity.

export const FilingStatus = "draft" as const

// Add missing methods to api object via augmentation — will be merged in client.ts
