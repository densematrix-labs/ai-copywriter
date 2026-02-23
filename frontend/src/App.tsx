import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useTokenStore } from './store/tokenStore'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import PricingPage from './pages/PricingPage'
import PaymentSuccessPage from './pages/PaymentSuccessPage'

function App() {
  const fetchStatus = useTokenStore((state) => state.fetchStatus)

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/payment/success" element={<PaymentSuccessPage />} />
      </Routes>
    </Layout>
  )
}

export default App
