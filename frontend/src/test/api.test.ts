import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock fingerprint before importing api
vi.mock('../lib/fingerprint', () => ({
  getDeviceId: vi.fn().mockResolvedValue('test-device-id'),
}))

import { generateCopy, getDeviceStatus, createCheckout } from '../lib/api'

describe('API functions', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  describe('generateCopy', () => {
    it('handles successful response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          variations: [{ id: 1, content: 'Test copy', word_count: 2 }],
          copy_type: 'marketing',
          remaining_generations: 5,
          is_free_trial: true,
        }),
      })

      const result = await generateCopy('marketing', 'test topic', 'professional', 'en', 3)
      
      expect(result.success).toBe(true)
      expect(result.variations).toHaveLength(1)
    })

    it('handles string error detail', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Something went wrong' }),
      })

      await expect(generateCopy('marketing', 'test', 'pro', 'en', 1))
        .rejects.toThrow('Something went wrong')
    })

    it('handles object error detail with error field', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'No tokens remaining', code: 'payment_required' },
        }),
      })

      await expect(generateCopy('marketing', 'test', 'pro', 'en', 1))
        .rejects.toThrow('No tokens remaining')
    })

    it('handles object error detail with message field', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          detail: { message: 'Invalid input' },
        }),
      })

      await expect(generateCopy('marketing', 'test', 'pro', 'en', 1))
        .rejects.toThrow('Invalid input')
    })

    it('never throws [object Object]', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'No tokens', code: 'err' },
        }),
      })

      try {
        await generateCopy('marketing', 'test', 'pro', 'en', 1)
      } catch (e) {
        expect((e as Error).message).not.toContain('[object Object]')
        expect((e as Error).message).not.toContain('object Object')
      }
    })
  })

  describe('getDeviceStatus', () => {
    it('returns device status', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          can_generate: true,
          remaining_generations: 3,
          is_free_trial: true,
          free_trial_limit: 3,
        }),
      })

      const result = await getDeviceStatus()
      
      expect(result.can_generate).toBe(true)
      expect(result.remaining_generations).toBe(3)
    })
  })

  describe('createCheckout', () => {
    it('returns checkout URL', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          checkout_url: 'https://checkout.creem.io/xxx',
          checkout_id: 'checkout_123',
        }),
      })

      const result = await createCheckout('pack_10', 'http://success', 'http://cancel')
      
      expect(result.checkout_url).toBe('https://checkout.creem.io/xxx')
    })

    it('handles checkout error with object detail', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          detail: { error: 'Invalid product' },
        }),
      })

      await expect(createCheckout('invalid', 'http://s', 'http://c'))
        .rejects.toThrow('Invalid product')
    })
  })
})
