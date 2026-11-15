import { describe, it, expect } from 'vitest'
import { bmiCategory, validationBadge } from '../lib/clinical'
import { nextActions } from '../lib/workflow'
describe('clinical',()=>{
  it('bmiCategory',()=>{ expect(bmiCategory(22)).toBe('Normal') })
  it('validationBadge',()=>{ expect(validationBadge('error')).toContain('red') })
  it('nextActions draft nurse',()=>{ expect(nextActions('draft','nurse')).toContain('submit') })
})
