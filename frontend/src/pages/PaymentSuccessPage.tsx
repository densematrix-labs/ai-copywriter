import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { useTokenStore } from '../store/tokenStore'

export default function PaymentSuccessPage() {
  const { t } = useTranslation()
  const { fetchStatus, status } = useTokenStore()

  useEffect(() => {
    // Refresh token status after payment
    fetchStatus()
  }, [fetchStatus])

  return (
    <div className="min-h-[60vh] flex items-center justify-center py-12">
      <div className="max-w-md mx-auto px-4 text-center">
        <div className="mb-8">
          <span className="inline-block text-6xl animate-bounce">🎉</span>
        </div>

        <h1 className="editorial-heading text-3xl text-navy-900 mb-4">
          {t('paymentSuccess.title')}
        </h1>

        <p className="text-navy-600 mb-6">
          {t('paymentSuccess.description')}
        </p>

        {status && (
          <div className="card p-6 mb-8">
            <div className="text-4xl font-display font-bold text-coral-500">
              {status.remaining_generations}
            </div>
            <p className="text-sm text-navy-500 mt-2">
              {t('status.remaining', { count: status.remaining_generations })}
            </p>
          </div>
        )}

        <Link to="/" className="btn btn-primary">
          {t('paymentSuccess.continue')}
        </Link>
      </div>
    </div>
  )
}
