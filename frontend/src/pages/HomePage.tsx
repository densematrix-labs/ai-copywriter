import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { generateCopy, CopyVariation } from '../lib/api'
import { useTokenStore } from '../store/tokenStore'

const copyTypes = [
  { id: 'marketing', icon: '📣', color: 'coral' },
  { id: 'product', icon: '🛍️', color: 'navy' },
  { id: 'ad', icon: '📱', color: 'coral' },
  { id: 'email', icon: '📧', color: 'navy' },
  { id: 'social', icon: '📲', color: 'coral' },
  { id: 'blog', icon: '📝', color: 'navy' },
]

const tones = ['professional', 'casual', 'humorous', 'urgent', 'luxury']

export default function HomePage() {
  const { t, i18n } = useTranslation()
  const [selectedType, setSelectedType] = useState<string>('marketing')
  const [topic, setTopic] = useState('')
  const [tone, setTone] = useState('professional')
  const [variations, setVariations] = useState(3)
  const [results, setResults] = useState<CopyVariation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<number | null>(null)

  const { status, decrementRemaining, fetchStatus } = useTokenStore()

  const handleGenerate = async () => {
    if (!topic.trim()) return
    
    setLoading(true)
    setError(null)
    setResults([])

    try {
      const response = await generateCopy(
        selectedType,
        topic,
        tone,
        i18n.language,
        variations
      )
      setResults(response.variations)
      decrementRemaining()
      fetchStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.failed'))
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async (text: string, id: number) => {
    await navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="py-12 sm:py-20">
      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center mb-16">
        <h1 className="editorial-heading text-4xl sm:text-5xl lg:text-6xl text-navy-900 mb-6 animate-fade-in">
          {t('hero.title')}
        </h1>
        <p className="editorial-body text-xl text-navy-600 max-w-2xl mx-auto mb-8 animate-slide-up">
          {t('hero.subtitle')}
        </p>
        <div className="flex items-center justify-center space-x-2 text-sm text-navy-500 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <span className="flex -space-x-2">
            {['😊', '🎯', '💡'].map((emoji, i) => (
              <span key={i} className="w-8 h-8 rounded-full bg-navy-100 flex items-center justify-center text-lg border-2 border-cream-50">
                {emoji}
              </span>
            ))}
          </span>
          <span>{t('hero.trusted')}</span>
        </div>
      </section>

      {/* Generator */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="card p-6 sm:p-8">
          {/* Copy Type Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-navy-700 mb-4">
              {t('generator.selectType')}
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {copyTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedType === type.id
                      ? 'border-coral-400 bg-coral-50'
                      : 'border-navy-100 hover:border-navy-200 bg-white'
                  }`}
                >
                  <span className="text-2xl block mb-2">{type.icon}</span>
                  <span className="text-xs font-medium text-navy-700">
                    {t(`copyTypes.${type.id}`)}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Topic Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-navy-700 mb-2">
              {t('generator.topic')}
            </label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder={t('generator.topicPlaceholder')}
              className="textarea h-24"
              data-testid="topic-input"
            />
          </div>

          {/* Options Row */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            {/* Tone */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-navy-700 mb-2">
                {t('generator.tone')}
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="input"
              >
                {tones.map((t_tone) => (
                  <option key={t_tone} value={t_tone}>
                    {t(`generator.tones.${t_tone}`)}
                  </option>
                ))}
              </select>
            </div>

            {/* Variations */}
            <div className="w-32">
              <label className="block text-sm font-medium text-navy-700 mb-2">
                {t('generator.variations')}
              </label>
              <select
                value={variations}
                onChange={(e) => setVariations(Number(e.target.value))}
                className="input"
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim() || (status !== null && !status.can_generate)}
            className="btn btn-primary w-full text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
            data-testid="generate-btn"
          >
            {loading ? (
              <span className="flex items-center justify-center space-x-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>{t('generator.generating')}</span>
              </span>
            ) : (
              t('generator.generate')
            )}
          </button>

          {/* No credits CTA */}
          {status && !status.can_generate && (
            <div className="mt-4 p-4 bg-coral-50 rounded-lg text-center">
              <p className="text-coral-700 mb-2">{t('errors.noCredits')}</p>
              <Link to="/pricing" className="btn btn-secondary">
                {t('nav.pricing')}
              </Link>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="mt-8 space-y-4" data-testid="results">
            <h2 className="font-display font-bold text-xl text-navy-900">
              {t('generator.results')}
            </h2>
            {results.map((variation) => (
              <div key={variation.id} className="card p-6 card-hover">
                <div className="flex justify-between items-start mb-4">
                  <span className="badge badge-navy">#{variation.id}</span>
                  <button
                    onClick={() => copyToClipboard(variation.content, variation.id)}
                    className="text-sm text-navy-500 hover:text-coral-500 transition-colors flex items-center space-x-1"
                  >
                    <span>{copiedId === variation.id ? t('generator.copied') : t('generator.copy')}</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
                <div className="prose prose-navy max-w-none font-mono text-sm whitespace-pre-wrap">
                  {variation.content}
                </div>
                <div className="mt-4 text-xs text-navy-400">
                  {variation.word_count} words
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* SEO Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 mt-20">
        <div className="text-center mb-12">
          <h2 className="editorial-heading text-3xl text-navy-900 mb-4">
            The Best Copy.ai Alternative
          </h2>
          <p className="text-navy-600 max-w-2xl mx-auto">
            Looking for a free Copy.ai alternative? Our AI copywriter generates high-converting 
            marketing copy, product descriptions, and ad text without the expensive subscription.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            { icon: '⚡', title: 'Instant Results', desc: 'Generate copy in seconds, not hours' },
            { icon: '🌍', title: '7 Languages', desc: 'Create content in English, Chinese, Japanese, German, French, Korean, Spanish' },
            { icon: '💰', title: 'Pay As You Go', desc: 'No subscriptions. Buy what you need.' },
          ].map((feature, i) => (
            <div key={i} className="text-center">
              <span className="text-4xl block mb-4">{feature.icon}</span>
              <h3 className="font-display font-bold text-navy-900 mb-2">{feature.title}</h3>
              <p className="text-navy-600 text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
