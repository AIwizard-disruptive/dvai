import { cn } from '@/lib/utils'

interface DVLogoProps {
  variant?: 'symbol' | 'wordmark'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeMap = {
  sm: 'h-6',
  md: 'h-8',
  lg: 'h-12',
  xl: 'h-16'
}

export function DVLogo({ variant = 'wordmark', size = 'md', className }: DVLogoProps) {
  const logoSrc = variant === 'wordmark' ? '/dv-wordmark.png' : '/dv-logo.png'
  
  return (
    <img
      src={logoSrc}
      alt="Disruptive Ventures"
      className={cn(sizeMap[size], 'w-auto object-contain', className)}
      data-theme="preserve"
    />
  )
}


