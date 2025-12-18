import { AdminAlert } from '@/components/admin-alert'
import { Providers } from '@/components/providers'
import { ThemeScript } from '@/components/theme-script'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'Disruptive Ventures - Command Center',
  description: 'Strategic intelligence system for venture operations',
  icons: {
    icon: '/dv-wordmark.png',
    apple: '/dv-wordmark.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className="antialiased">
        <Providers>
          <AdminAlert />
          {children}
        </Providers>
      </body>
    </html>
  )
}



