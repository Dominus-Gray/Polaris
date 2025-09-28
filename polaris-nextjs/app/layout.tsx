import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'sonner'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Polaris - Business Assessment & Professional Services Platform',
  description: 'Comprehensive business assessment platform with tier-based evaluations, professional services marketplace, and AI-powered guidance.',
  keywords: 'business assessment, procurement readiness, professional services, compliance, business consulting',
  authors: [{ name: 'Polaris Platform' }],
  openGraph: {
    title: 'Polaris - Business Assessment Platform',
    description: 'Comprehensive business assessment platform with tier-based evaluations and professional services.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Polaris - Business Assessment Platform',
    description: 'Comprehensive business assessment platform with tier-based evaluations and professional services.',
  },
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster position="top-right" richColors />
        </Providers>
      </body>
    </html>
  )
}