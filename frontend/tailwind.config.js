/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
        extend: {
                borderRadius: {
                        lg: 'var(--radius)',
                        md: 'calc(var(--radius) - 2px)',
                        sm: 'calc(var(--radius) - 4px)'
                },
                colors: {
                        // Polaris Harmonious Blue System
                        polaris: {
                          // Core Blue Family - Gentle Gradations
                          'blue-50': '#F0F6FF',
                          'blue-100': '#E0EDFF', 
                          'blue-200': '#C7DDFF',
                          'blue-300': '#A4C7FF',
                          'blue-400': '#7BA7FF',
                          'blue-500': '#4F88FF',  // Primary
                          'blue-600': '#3366CC',
                          'blue-700': '#2952A3',
                          'blue-800': '#1E3D7A',
                          'blue-900': '#152952',
                          
                          // Complementary Grays (blue undertones)
                          'gray-50': '#F8F9FB',
                          'gray-100': '#F1F3F7',
                          'gray-200': '#E4E8EF',
                          'gray-300': '#D1D7E0',
                          'gray-400': '#9BA5B8',
                          'gray-500': '#6B7894',
                          'gray-600': '#4A5568',
                          'gray-700': '#2D3748',
                          'gray-800': '#1A202C',
                          'gray-900': '#171923',
                          
                          // Minimal Accents
                          'success': '#10B981',
                          'success-light': '#D1FAE5',
                          'warning': '#F59E0B',
                          'warning-light': '#FEF3C7',
                          'danger': '#EF4444',
                          'danger-light': '#FEE2E2',
                        },
                        // Existing shadcn/ui colors
                        background: 'hsl(var(--background))',
                        foreground: 'hsl(var(--foreground))',
                        card: {
                                DEFAULT: 'hsl(var(--card))',
                                foreground: 'hsl(var(--card-foreground))'
                        },
                        popover: {
                                DEFAULT: 'hsl(var(--popover))',
                                foreground: 'hsl(var(--popover-foreground))'
                        },
                        primary: {
                                DEFAULT: 'hsl(var(--primary))',
                                foreground: 'hsl(var(--primary-foreground))'
                        },
                        secondary: {
                                DEFAULT: 'hsl(var(--secondary))',
                                foreground: 'hsl(var(--secondary-foreground))'
                        },
                        muted: {
                                DEFAULT: 'hsl(var(--muted))',
                                foreground: 'hsl(var(--muted-foreground))'
                        },
                        accent: {
                                DEFAULT: 'hsl(var(--accent))',
                                foreground: 'hsl(var(--accent-foreground))'
                        },
                        destructive: {
                                DEFAULT: 'hsl(var(--destructive))',
                                foreground: 'hsl(var(--destructive-foreground))'
                        },
                        border: 'hsl(var(--border))',
                        input: 'hsl(var(--input))',
                        ring: 'hsl(var(--ring))',
                        chart: {
                                '1': 'hsl(var(--chart-1))',
                                '2': 'hsl(var(--chart-2))',
                                '3': 'hsl(var(--chart-3))',
                                '4': 'hsl(var(--chart-4))',
                                '5': 'hsl(var(--chart-5))'
                        }
                },
                keyframes: {
                        'accordion-down': {
                                from: {
                                        height: '0'
                                },
                                to: {
                                        height: 'var(--radix-accordion-content-height)'
                                }
                        },
                        'accordion-up': {
                                from: {
                                        height: 'var(--radix-accordion-content-height)'
                                },
                                to: {
                                        height: '0'
                                }
                        }
                },
                animation: {
                        'accordion-down': 'accordion-down 0.2s ease-out',
                        'accordion-up': 'accordion-up 0.2s ease-out'
                }
        }
  },
  plugins: [require("tailwindcss-animate")],
};