import { getDeviceId } from './fingerprint'

const API_BASE = import.meta.env.PROD ? '' : ''

export interface CopyVariation {
  id: number
  content: string
  word_count: number
}

export interface GenerateResponse {
  success: boolean
  variations: CopyVariation[]
  copy_type: string
  remaining_generations: number | null
  is_free_trial: boolean
}

export interface DeviceStatus {
  can_generate: boolean
  remaining_generations: number
  is_free_trial: boolean
  free_trial_limit: number
}

export interface Product {
  sku: string
  name: string
  generations: number
  price_cents: number
  price_display: string
  per_generation: string
}

export interface CheckoutResponse {
  checkout_url: string
  checkout_id: string
}

export async function generateCopy(
  copyType: string,
  topic: string,
  tone: string,
  language: string,
  variations: number
): Promise<GenerateResponse> {
  const deviceId = await getDeviceId()
  
  const response = await fetch(`${API_BASE}/api/v1/copy/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      copy_type: copyType,
      topic,
      tone,
      language,
      device_id: deviceId,
      variations
    })
  })
  
  if (!response.ok) {
    const data = await response.json()
    const errorMessage = typeof data.detail === 'string' 
      ? data.detail 
      : data.detail?.error || data.detail?.message || 'Generation failed'
    throw new Error(errorMessage)
  }
  
  return response.json()
}

export async function getDeviceStatus(): Promise<DeviceStatus> {
  const deviceId = await getDeviceId()
  
  const response = await fetch(`${API_BASE}/api/v1/tokens/status/${deviceId}`)
  
  if (!response.ok) {
    throw new Error('Failed to fetch status')
  }
  
  return response.json()
}

export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE}/api/v1/payment/products`)
  
  if (!response.ok) {
    throw new Error('Failed to fetch products')
  }
  
  const data = await response.json()
  return data.products
}

export async function createCheckout(
  productSku: string,
  successUrl: string,
  cancelUrl: string
): Promise<CheckoutResponse> {
  const deviceId = await getDeviceId()
  
  const response = await fetch(`${API_BASE}/api/v1/payment/create-checkout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_sku: productSku,
      device_id: deviceId,
      success_url: successUrl,
      cancel_url: cancelUrl
    })
  })
  
  if (!response.ok) {
    const data = await response.json()
    const errorMessage = typeof data.detail === 'string' 
      ? data.detail 
      : data.detail?.error || data.detail?.message || 'Checkout failed'
    throw new Error(errorMessage)
  }
  
  return response.json()
}
