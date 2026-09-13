'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useHashRoute } from '@/lib/router'
import { AppProvider } from './LangContext'
import { Header } from './Header'
import { Footer } from './Footer'
import { CartDrawer } from './CartDrawer'
import { useCategories } from './hooks'
import { HomeView } from './HomeView'
import { CategoryView } from './CategoryView'
import { ProductView } from './ProductView'
import { CheckoutView, SuccessView } from './CheckoutView'
import { LoginView, RegisterView } from './AuthViews'
import { OrdersView, AccountView } from './OrdersView'
import { PrescriptionView } from './PrescriptionView'
import { AssistantView } from './AssistantView'
import { InteractionsView } from './InteractionsView'
import { AdminView } from './AdminView'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
})

function Shell() {
  const [route] = useHashRoute()
  const { data: categories = [] } = useCategories()

  const content = (() => {
    const { view, params } = route
    switch (view) {
      case 'home': return <HomeView />
      case 'c': return <CategoryView key={params[0]} categorySlug={params[0]} />
      case 'search': return <CategoryView key={params[0]} searchQuery={decodeURIComponent(params[0] || '')} />
      case 'p': return <ProductView slug={params[0]} />
      case 'cart': return <CheckoutView />
      case 'checkout': return <CheckoutView />
      case 'success': return <SuccessView orderId={params[0]} />
      case 'login': return <LoginView />
      case 'register': return <RegisterView />
      case 'orders': return <OrdersView />
      case 'account': return <AccountView />
      case 'prescription': return <PrescriptionView />
      case 'assistant': return <AssistantView />
      case 'interactions': return <InteractionsView />
      case 'admin': return <AdminView />
      default: return <HomeView />
    }
  })()

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header categories={categories} />
      <main className="flex-1 w-full">{content}</main>
      <Footer />
      <CartDrawer />
    </div>
  )
}

export default function PharmacyApp() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <Shell />
      </AppProvider>
    </QueryClientProvider>
  )
}
