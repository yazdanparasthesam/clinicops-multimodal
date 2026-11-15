import { describe, it, expect, vi, beforeAll } from 'vitest'
describe('client smoke',()=>{
  it('constructs base',()=>{
    expect(import.meta.env).toBeDefined();
  })
})
