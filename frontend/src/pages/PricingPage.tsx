import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getProducts, createCheckout, Product } from '../lib/api'

export default function PricingPage() {
  const { t } = useTranslation()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      const data = await getProducts()
      setProducts(data)
    } catch (err) {
      setError('Failed to load products')
    } finally {
      setLoading(false)
    }
  }

  const handleBuy = async (sku: string) => {
    setCheckoutLoading(sku)
    setError(null)

    try {
      const baseUrl = window.location.origin
      const { checkout_url } = await createCheckout(
        sku,
        `${baseUrl}/payment/success`,
        `${baseUrl}/pricing`
      )
      window.location.href = checkout_url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Checkout failed')
      setCheckoutLoading(null)
    }
  }

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-coral-400 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="py-12 sm:py-20">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="editorial-heading text-4xl sm:text-5xl text-navy-900 mb-4">
            {t('pricing.title')}
          </h1>
          <p className="text-xl text-navy-600">
            {t('pricing.subtitle')}
          </p>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-50 rounded-lg text-red-700 text-center">
            {error}
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {products.map((product, index) => (
            <div
              key={product.sku}
              className={`card p-8 relative ${
                index === 1 ? 'border-2 border-coral-400 scale-105' : ''
              }`}
            >
              {index === 1 && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="badge badge-coral px-4 py-1">
                    {t('pricing.popular')}
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="font-display font-bold text-xl text-navy-900 mb-2">
                  {product.name}
                </h3>
                <div className="text-4xl font-display font-bold text-coral-500 mb-2">
                  {product.price_display}
                </div>
                <p className="text-sm text-navy-500">
                  {t('pricing.generations', { count: product.generations })}
                </p>
                <p className="text-xs text-navy-400 mt-1">
                  {t('pricing.perGeneration', { price: product.per_generation })}
                </p>
              </div>

              <ul className="space-y-3 mb-8">
                {['noExpiry', 'allTypes', 'languages', 'support'].map((feature) => (
                  <li key={feature} className="flex items-center text-sm text-navy-600">
                    <svg className="w-5 h-5 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {t(`pricing.features.${feature}`)}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleBuy(product.sku)}
                disabled={checkoutLoading === product.sku}
                className={`btn w-full ${
                  index === 1 ? 'btn-primary' : 'btn-outline'
                } disabled:opacity-50`}
              >
                {checkoutLoading === product.sku ? (
                  <span className="flex items-center justify-center space-x-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  </span>
                ) : (
                  t('pricing.buy')
                )}
              </button>
            </div>
          ))}
        </div>

        {/* Trust badges */}
        <div className="mt-16 text-center">
          <p className="text-sm text-navy-500 mb-4">Secure payment powered by</p>
          <div className="flex items-center justify-center space-x-8">
            <span className="text-navy-400 font-medium">🔒 SSL Secured</span>
            <span className="text-navy-400 font-medium">💳 Creem</span>
            <span className="text-navy-400 font-medium">🌍 Global Payments</span>
          </div>
        </div>
      </div>
    </div>
  )
}
