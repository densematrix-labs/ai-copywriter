import FingerprintJS from '@fingerprintjs/fingerprintjs'

let cachedDeviceId: string | null = null

export async function getDeviceId(): Promise<string> {
  if (cachedDeviceId) {
    return cachedDeviceId
  }

  // Try to get from localStorage first
  const stored = localStorage.getItem('device_id')
  if (stored) {
    cachedDeviceId = stored
    return stored
  }

  // Generate new fingerprint
  try {
    const fp = await FingerprintJS.load()
    const result = await fp.get()
    cachedDeviceId = result.visitorId
    localStorage.setItem('device_id', cachedDeviceId)
    return cachedDeviceId
  } catch (error) {
    // Fallback to random ID
    cachedDeviceId = `fallback_${Math.random().toString(36).substring(2)}${Date.now()}`
    localStorage.setItem('device_id', cachedDeviceId)
    return cachedDeviceId
  }
}
