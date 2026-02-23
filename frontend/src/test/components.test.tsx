import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from '../components/Layout'
import LanguageSwitcher from '../components/LanguageSwitcher'

// Mock token store
vi.mock('../store/tokenStore', () => ({
  useTokenStore: () => ({
    status: {
      can_generate: true,
      remaining_generations: 5,
      is_free_trial: true,
      free_trial_limit: 3,
    },
  }),
}))

describe('Layout', () => {
  it('renders children', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div data-testid="child">Test Content</div>
        </Layout>
      </BrowserRouter>
    )

    expect(screen.getByTestId('child')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Content</div>
        </Layout>
      </BrowserRouter>
    )

    expect(screen.getByText('nav.home')).toBeInTheDocument()
    expect(screen.getByText('nav.pricing')).toBeInTheDocument()
  })

  it('shows remaining generations', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Content</div>
        </Layout>
      </BrowserRouter>
    )

    expect(screen.getByText('status.remaining')).toBeInTheDocument()
  })
})

describe('LanguageSwitcher', () => {
  it('renders language button', () => {
    render(
      <BrowserRouter>
        <LanguageSwitcher />
      </BrowserRouter>
    )

    expect(screen.getByLabelText('Switch language')).toBeInTheDocument()
  })
})
