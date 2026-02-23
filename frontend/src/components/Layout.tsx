import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'
import { useTokenStore } from '../store/tokenStore'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { t } = useTranslation()
  const location = useLocation()
  const status = useTokenStore((state) => state.status)

  return (
    <div className="min-h-screen flex flex-col grain-overlay">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-cream-50/80 backdrop-blur-md border-b border-navy-100/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-2xl">✍️</span>
              <span className="font-display font-bold text-navy-900 text-lg">
                {t('app.name')}
              </span>
            </Link>

            {/* Nav */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link 
                to="/" 
                className={`font-medium transition-colors ${
                  location.pathname === '/' 
                    ? 'text-coral-500' 
                    : 'text-navy-600 hover:text-navy-900'
                }`}
              >
                {t('nav.home')}
              </Link>
              <Link 
                to="/pricing" 
                className={`font-medium transition-colors ${
                  location.pathname === '/pricing' 
                    ? 'text-coral-500' 
                    : 'text-navy-600 hover:text-navy-900'
                }`}
              >
                {t('nav.pricing')}
              </Link>
            </nav>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              {status && (
                <div className="hidden sm:flex items-center space-x-2 text-sm">
                  <span className={`badge ${status.is_free_trial ? 'badge-coral' : 'badge-navy'}`}>
                    {status.is_free_trial ? t('status.freeTrial') : ''}
                  </span>
                  <span className="text-navy-600">
                    {t('status.remaining', { count: status.remaining_generations })}
                  </span>
                </div>
              )}
              <LanguageSwitcher />
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-navy-900 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex items-center space-x-2">
              <span className="text-xl">✍️</span>
              <span className="font-display font-bold">{t('app.name')}</span>
            </div>
            
            <div className="flex items-center space-x-6 text-sm text-navy-300">
              <Link to="/privacy" className="hover:text-white transition-colors">
                {t('footer.privacy')}
              </Link>
              <Link to="/terms" className="hover:text-white transition-colors">
                {t('footer.terms')}
              </Link>
            </div>
            
            <div className="text-sm text-navy-400">
              {t('footer.madeWith')} ❤️ {t('footer.by')}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
