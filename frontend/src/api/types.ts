export type Visit = { id:number; patient_name:string; patient_dob?:string; status:string; created_by:number; created_at:string; deadline_at?:string; scores?:any; checklist?:any; notes_draft?:string; transcript?:string; vision_finding?:string }
export type Validation = { rule_id:string; severity:string; message:string; field?:string }
export type Attachment = { id:number; visit_id:number; kind:string; filename:string; mime:string; size:number; sha256:string }
