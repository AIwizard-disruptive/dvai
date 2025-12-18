/**
 * This script runs BEFORE React hydrates to prevent the white flash
 * It must be inlined in the HTML head
 */
export function ThemeScript() {
  const themeScript = `
    (function() {
      const storageKey = 'dv-theme';
      const defaultTheme = 'dark';
      
      try {
        const stored = localStorage.getItem(storageKey);
        const theme = stored === 'light' || stored === 'dark' ? stored : defaultTheme;
        
        document.documentElement.classList.add(theme);
      } catch (e) {
        console.error('Failed to load theme:', e);
        document.documentElement.classList.add(defaultTheme);
      }
    })();
  `

  return (
    <script
      dangerouslySetInnerHTML={{ __html: themeScript }}
      suppressHydrationWarning
    />
  )
}


