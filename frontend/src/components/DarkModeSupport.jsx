import React, { createContext, useContext, useState, useEffect } from 'react';

// Dark Mode Context
const DarkModeContext = createContext();

// Dark Mode Provider Component
export function DarkModeProvider({ children }) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSystemDark, setIsSystemDark] = useState(false);
  const [userPreference, setUserPreference] = useState('system'); // 'light', 'dark', 'system'

  useEffect(() => {
    // Check system preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsSystemDark(mediaQuery.matches);

    // Load user preference
    const savedPreference = localStorage.getItem('polaris_theme') || 'system';
    setUserPreference(savedPreference);

    // Set initial dark mode state
    const shouldBeDark = 
      savedPreference === 'dark' || 
      (savedPreference === 'system' && mediaQuery.matches);
    
    setIsDarkMode(shouldBeDark);
    applyDarkMode(shouldBeDark);

    // Listen for system theme changes
    const handleSystemThemeChange = (e) => {
      setIsSystemDark(e.matches);
      if (userPreference === 'system') {
        setIsDarkMode(e.matches);
        applyDarkMode(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, []);

  const applyDarkMode = (dark) => {
    if (dark) {
      document.documentElement.classList.add('dark');
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = 'light';
    }
  };

  const setTheme = (theme) => {
    setUserPreference(theme);
    localStorage.setItem('polaris_theme', theme);

    let shouldBeDark = false;
    if (theme === 'dark') {
      shouldBeDark = true;
    } else if (theme === 'system') {
      shouldBeDark = isSystemDark;
    }

    setIsDarkMode(shouldBeDark);
    applyDarkMode(shouldBeDark);
  };

  const value = {
    isDarkMode,
    userPreference,
    setTheme,
    isSystemDark
  };

  return (
    <DarkModeContext.Provider value={value}>
      {children}
    </DarkModeContext.Provider>
  );
}

// Hook to use dark mode context
export function useDarkMode() {
  const context = useContext(DarkModeContext);
  if (!context) {
    throw new Error('useDarkMode must be used within a DarkModeProvider');
  }
  return context;
}

// Dark Mode Toggle Component
export function DarkModeToggle() {
  const { isDarkMode, userPreference, setTheme } = useDarkMode();
  const [showOptions, setShowOptions] = useState(false);

  const themeOptions = [
    { 
      id: 'light', 
      label: 'Light Mode', 
      icon: '☀️',
      description: 'Always use light theme'
    },
    { 
      id: 'dark', 
      label: 'Dark Mode', 
      icon: '🌙',
      description: 'Always use dark theme'
    },
    { 
      id: 'system', 
      label: 'System Default', 
      icon: '🖥️',
      description: 'Follow system preference'
    }
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setShowOptions(!showOptions)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        title={`Current theme: ${userPreference}`}
      >
        <span className="text-lg">
          {userPreference === 'light' ? '☀️' : 
           userPreference === 'dark' ? '🌙' : 
           isDarkMode ? '🌙' : '☀️'}
        </span>
        <span className="hidden sm:inline text-sm text-slate-600 dark:text-slate-300">
          Theme
        </span>
      </button>

      {showOptions && (
        <>
          <div className="absolute top-full right-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
            <div className="p-2">
              <div className="px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
                Choose Theme
              </div>
              {themeOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    setTheme(option.id);
                    setShowOptions(false);
                  }}
                  className={`w-full flex items-start gap-3 px-3 py-3 text-left rounded-lg transition-colors ${
                    userPreference === option.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                  }`}
                >
                  <span className="text-lg">{option.icon}</span>
                  <div>
                    <div className="font-medium">{option.label}</div>
                    <div className="text-xs opacity-75">{option.description}</div>
                  </div>
                  {userPreference === option.id && (
                    <svg className="w-4 h-4 ml-auto mt-0.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setShowOptions(false)}
          />
        </>
      )}
    </div>
  );
}

// Dark Mode Optimized Components
export function DarkModeCard({ children, className = '', ...props }) {
  return (
    <div 
      className={`bg-white border border-gray-200 text-gray-900 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function DarkModeButton({ 
  children, 
  variant = 'primary', 
  className = '', 
  ...props 
}) {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white',
    secondary: 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-900 dark:text-slate-100',
    outline: 'border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
  };

  return (
    <button 
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function DarkModeInput({ 
  className = '', 
  ...props 
}) {
  return (
    <input 
      className={`w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${className}`}
      {...props}
    />
  );
}