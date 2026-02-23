import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { getDeviceStatus, DeviceStatus } from '../lib/api'

interface TokenState {
  status: DeviceStatus | null
  loading: boolean
  error: string | null
  fetchStatus: () => Promise<void>
  decrementRemaining: () => void
}

export const useTokenStore = create<TokenState>()(
  persist(
    (set, get) => ({
      status: null,
      loading: false,
      error: null,
      
      fetchStatus: async () => {
        set({ loading: true, error: null })
        try {
          const status = await getDeviceStatus()
          set({ status, loading: false })
        } catch (error) {
          set({ error: 'Failed to fetch status', loading: false })
        }
      },
      
      decrementRemaining: () => {
        const { status } = get()
        if (status && status.remaining_generations > 0) {
          set({
            status: {
              ...status,
              remaining_generations: status.remaining_generations - 1
            }
          })
        }
      }
    }),
    {
      name: 'token-storage',
      partialize: (state) => ({ status: state.status })
    }
  )
)
