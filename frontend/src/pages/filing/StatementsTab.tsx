// @ts-nocheck
import { useState, type ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../api/client'
import ErrorNote from '../../components/ErrorNote'
import { fmtScore } from '../../lib/format'
import { scoreLabel } from '../../lib/categories'
import type { VisitStatus, ClinicalScore, AssessmentData, VitalsData } from '../../api/types'

const VITALS_ORDER: { key: string; subtotal?: string }[] = [
  { key: 'blood_pressure' }, { key: 'heart_rate' }, { key: 'temperature' },
  { key: 'respiratory_rate' }, { key: 'oxygen_saturation', subtotal: 'VITALS SUMMARY' },
]
const ASSESSMENT_ORDER: { key: string; subtotal?: string }[] = [
  { key: 'chief_complaint' }, { key: 'history' }, { key: 'examination' },
  { key: 'labs' }, { key: 'imaging', subtotal: 'ASSESSMENT SUMMARY' },
]

function AssessmentView({ data, order }: { data: AssessmentData; order: typeof VITALS_ORDER }) {
  return (
    <table className="w-full">
      <tbody>
        {order.map(({ key, subtotal }) => {
          const node = data[key]
          if (node && typeof node === 'object' && 'items' in node) {
            const section = node as { items: { code: string; name: string; value: number; unit?: string }[]; total?: number }
            return (
              <FragmentRow key={key} label={scoreLabel(key)}>
                {section.items.map((it) => (
                  <tr key={it.code}><td className="td pl-8 text-slate-500">{it.code} · {it.name}</td>
                    <td className="td text-right text-slate-500">{fmtScore(it.value, it.unit)}</td></tr>
                ))}
                {section.total !== undefined && (
                  <tr><td className="td font-semibold">Total {scoreLabel(key)}</td>
                    <td className="td text-right font-semibold">{fmtScore(section.total)}</td></tr>
                )}
              </FragmentRow>
            )
          }
          if (typeof node === 'number') {
            return (
              <tr key={key} className={subtotal?.startsWith('TOTAL') || subtotal === 'VITALS SUMMARY' ? 'bg-brand-50' : ''}>
                <td className={`td ${subtotal ? 'font-semibold' : ''}`}>{subtotal ?? scoreLabel(key)}</td>
                <td className={`td text-right ${subtotal ? 'font-semibold' : ''}`}>{fmtScore(node)}</td>
              </tr>
            )
          }
          return null
        })}
      </tbody>
    </table>
  )
}

function FragmentRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <>
      <tr className="bg-slate-50"><td className="td font-semibold uppercase text-xs tracking-wide text-slate-600" colSpan={2}>{label}</td></tr>
      {children}
    </>
  )
}

const SCORE_LABELS: Record<string, string> = {
  triage_score: 'Triage score',
  early_warning: 'Early Warning Score',
  pain_scale: 'Pain scale',
  risk_index: 'Clinical risk index',
}

/** Vitals timeline — deterministic, captured from intake attachments + manual entry. */
function VitalsView({ vitals }: { vitals: VitalsData }) {
  const line = (label: string, value: number | string, strong = false) => (
    <tr key={label}>
      <td className={`td ${strong ? 'font-semibold' : ''}`}>{label}</td>
      <td className={`td text-right ${strong ? 'font-semibold' : ''}`}>{typeof value === 'number' ? fmtScore(value) : value}</td>
    </tr>
  )
  const stable = vitals.flags?.length === 0
  return (
    <table className="w-full">
      <tbody>
        <FragmentRow label="Vitals (latest intake)">
          {line('Blood pressure', vitals.blood_pressure ?? '—')}
          {line('Heart rate', vitals.heart_rate ?? '—')}
          {line('Temperature', vitals.temperature ?? '—')}
          {line('Respiratory rate', vitals.respiratory_rate ?? '—')}
          {line('SpO₂', vitals.oxygen_saturation ?? '—', true)}
        </FragmentRow>
        <FragmentRow label="Derived indicators">
          {line(SCORE_LABELS.early_warning, vitals.early_warning_score ?? '—')}
          {line(SCORE_LABELS.triage_score, vitals.triage_score ?? '—', true)}
        </FragmentRow>
        <tr>
          <td className="td">Validation flags (R001–R008)</td>
          <td className="td text-right">
            <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${stable ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
              {stable ? 'no flags ✓' : `${vitals.flags.length} flag(s) · review`}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  )
}

function fmtClinicalScore(r: ClinicalScore): string {
  if (r.value === null) return '—'
  return r.unit === '%' ? `${r.value}%` : `${r.value}${r.unit === 'x' ? '×' : r.unit ? ` ${r.unit}` : ''}`
}

/** Deterministic clinical scores — each row shows its formula so the math is auditable. */
function ScoresPanel({ scores }: { scores: ClinicalScore[] }) {
  return (
    <table className="w-full">
      <thead>
        <tr className="text-left text-xs uppercase tracking-wide text-slate-400">
          <th className="td">Score</th><th className="td text-right">Value</th>
          <th className="td">Formula</th><th className="td">Interpretation</th>
        </tr>
      </thead>
      <tbody>
        {scores.map((r) => (
          <tr key={r.key}>
            <td className="td font-medium text-slate-700">{r.label}</td>
            <td className="td text-right font-semibold tabular-nums">{fmtClinicalScore(r)}</td>
            <td className="td font-mono text-xs text-slate-500">{r.formula}</td>
            <td className="td text-xs text-slate-500">{r.interpretation}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function ScoresTab({ visitId, status }: { visitId: number; status: VisitStatus }) {
  const qc = useQueryClient()
  const [error, setError] = useState<unknown>(null)
  const noRetry404 = { retry: (_c: number, e: unknown) => (e as { status?: number })?.status !== 404 }
  const vitalsQ = useQuery({ queryKey: ['vitals', visitId], queryFn: () => api.visits.getVitals(visitId), ...noRetry404 })
  const assessmentQ = useQuery({ queryKey: ['assessment', visitId], queryFn: () => api.visits.getAssessment(visitId), ...noRetry404 })
  const scoresQ = useQuery({ queryKey: ['scores', visitId], queryFn: () => api.visits.getScores(visitId), ...noRetry404 })
  const vitalsTimelineQ = useQuery({ queryKey: ['vitals-timeline', visitId], queryFn: () => api.visits.getVitalsTimeline(visitId), ...noRetry404 })
  const generate = useMutation({
    mutationFn: () => api.visits.generateScores(visitId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vitals', visitId] })
      qc.invalidateQueries({ queryKey: ['assessment', visitId] })
      qc.invalidateQueries({ queryKey: ['scores', visitId] })
      qc.invalidateQueries({ queryKey: ['vitals-timeline', visitId] })
    },
    onError: setError,
  })
  const editable = status === 'draft' || status === 'changes_requested'

  return (
    <div className="space-y-4">
      <ErrorNote error={error} />
      <div className="card flex items-center justify-between">
        <p className="text-sm text-slate-500">Deterministic generation from mapped intake — the AI never computes these figures.</p>
        <button className="btn-primary" disabled={generate.isPending || !editable} onClick={() => { setError(null); generate.mutate() }}>
          {generate.isPending ? 'Generating…' : 'Generate scores'}
        </button>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-2 font-semibold text-slate-700">Vitals {vitalsQ.data && <span className="text-xs text-slate-400">v{vitalsQ.data.version}</span>}</h3>
          {vitalsQ.data ? <AssessmentView data={vitalsQ.data} order={VITALS_ORDER} /> : <p className="text-sm text-slate-400">Not generated yet.</p>}
        </div>
        <div className="card">
          <h3 className="mb-2 font-semibold text-slate-700">Assessment {assessmentQ.data && <span className="text-xs text-slate-400">v{assessmentQ.data.version}</span>}</h3>
          {assessmentQ.data ? <AssessmentView data={assessmentQ.data} order={ASSESSMENT_ORDER} /> : <p className="text-sm text-slate-400">Not generated yet.</p>}
        </div>
        <div className="card">
          <h3 className="mb-2 font-semibold text-slate-700">
            Vitals timeline {vitalsTimelineQ.data && <span className="text-xs text-slate-400">v{vitalsTimelineQ.data.version}</span>}
          </h3>
          {vitalsTimelineQ.data
            ? <VitalsView vitals={vitalsTimelineQ.data.data as unknown as VitalsData} />
            : <p className="text-sm text-slate-400">Needs intake attachments — upload vitals or visit notes first.</p>}
        </div>
        <div className="card">
          <h3 className="mb-2 font-semibold text-slate-700">Clinical scores</h3>
          {scoresQ.data && scoresQ.data.length > 0
            ? <ScoresPanel scores={scoresQ.data} />
            : <p className="text-sm text-slate-400">Generated with the assessment — every score shows its formula.</p>}
        </div>
      </div>
    </div>
  )
}
