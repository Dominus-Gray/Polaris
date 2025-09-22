import React, { createContext, useContext, useState, useEffect } from 'react';

// Language Context
const LanguageContext = createContext();

// Translation dictionaries
const translations = {
  en: {
    // Common
    'welcome': 'Welcome',
    'loading': 'Loading...',
    'save': 'Save',
    'cancel': 'Cancel',
    'submit': 'Submit',
    'continue': 'Continue',
    'back': 'Back',
    'next': 'Next',
    'previous': 'Previous',
    'complete': 'Complete',
    'skip': 'Skip',
    
    // Navigation
    'dashboard': 'Dashboard',
    'assessment': 'Assessment',
    'services': 'Services',
    'knowledge_base': 'Knowledge Base',
    'profile': 'Profile',
    'settings': 'Settings',
    'logout': 'Logout',
    
    // Dashboard
    'procurement_readiness': 'Procurement Readiness',
    'assessment_complete': 'Assessment Complete',
    'critical_gaps': 'Critical Gaps',
    'active_services': 'Active Services',
    'readiness_score': 'Readiness Score',
    'overall_readiness': 'Overall Readiness',
    'recommended_next_steps': 'Recommended Next Steps',
    'recent_activity': 'Recent Activity',
    
    // Assessment
    'business_areas': 'Business Areas',
    'start_assessment': 'Start Assessment',
    'continue_assessment': 'Continue Assessment',
    'assessment_progress': 'Assessment Progress',
    'tier_access': 'Tier Access',
    'evidence_required': 'Evidence Required',
    
    // Onboarding
    'getting_started': 'Getting Started',
    'complete_onboarding': 'Complete Onboarding',
    'skip_guide': 'Skip Guide',
    'lets_begin': "Let's Begin",
    
    // AI Coach
    'ai_coach': 'AI Coach',
    'ask_anything': 'Ask me anything about procurement readiness...',
    'ai_thinking': 'AI Coach is thinking...',
    'online_ready': 'Online & Ready to Help',
    
    // Roles
    'client': 'Small Business Client',
    'provider': 'Service Provider',
    'navigator': 'Digital Navigator',
    'agency': 'Local Agency',
    
    // Success Messages
    'assessment_completed': 'Assessment completed successfully!',
    'profile_updated': 'Profile updated successfully!',
    'service_requested': 'Service request submitted successfully!',
    'great_progress': "You're making great progress!",
    'certification_ready': 'Certification Ready!',
    
    // Error Messages
    'error_occurred': 'An error occurred',
    'try_again': 'Please try again',
    'connection_error': 'Connection error - please check your internet',
    'invalid_input': 'Please check your input and try again'
  },
  es: {
    // Common
    'welcome': 'Bienvenido',
    'loading': 'Cargando...',
    'save': 'Guardar',
    'cancel': 'Cancelar',
    'submit': 'Enviar',
    'continue': 'Continuar',
    'back': 'Atrás',
    'next': 'Siguiente',
    'previous': 'Anterior',
    'complete': 'Completar',
    'skip': 'Omitir',
    
    // Navigation
    'dashboard': 'Panel de Control',
    'assessment': 'Evaluación',
    'services': 'Servicios',
    'knowledge_base': 'Base de Conocimientos',
    'profile': 'Perfil',
    'settings': 'Configuración',
    'logout': 'Cerrar Sesión',
    
    // Dashboard
    'procurement_readiness': 'Preparación para Contratación',
    'assessment_complete': 'Evaluación Completa',
    'critical_gaps': 'Brechas Críticas',
    'active_services': 'Servicios Activos',
    'readiness_score': 'Puntuación de Preparación',
    'overall_readiness': 'Preparación General',
    'recommended_next_steps': 'Próximos Pasos Recomendados',
    'recent_activity': 'Actividad Reciente',
    
    // Assessment
    'business_areas': 'Áreas de Negocio',
    'start_assessment': 'Comenzar Evaluación',
    'continue_assessment': 'Continuar Evaluación',
    'assessment_progress': 'Progreso de Evaluación',
    'tier_access': 'Acceso por Niveles',
    'evidence_required': 'Evidencia Requerida',
    
    // Onboarding
    'getting_started': 'Comenzando',
    'complete_onboarding': 'Completar Orientación',
    'skip_guide': 'Omitir Guía',
    'lets_begin': 'Comencemos',
    
    // AI Coach
    'ai_coach': 'Entrenador IA',
    'ask_anything': 'Pregúntame sobre preparación para contratación...',
    'ai_thinking': 'El Entrenador IA está pensando...',
    'online_ready': 'En Línea y Listo para Ayudar',
    
    // Roles
    'client': 'Cliente de Pequeña Empresa',
    'provider': 'Proveedor de Servicios',
    'navigator': 'Navegador Digital',
    'agency': 'Agencia Local',
    
    // Success Messages
    'assessment_completed': '¡Evaluación completada exitosamente!',
    'profile_updated': '¡Perfil actualizado exitosamente!',
    'service_requested': '¡Solicitud de servicio enviada exitosamente!',
    'great_progress': '¡Estás haciendo un gran progreso!',
    'certification_ready': '¡Listo para Certificación!',
    
    // Error Messages
    'error_occurred': 'Ocurrió un error',
    'try_again': 'Por favor intenta de nuevo',
    'connection_error': 'Error de conexión - verifica tu internet',
    'invalid_input': 'Verifica tu información e intenta de nuevo'
  },
  fr: {
    // Common
    'welcome': 'Bienvenue',
    'loading': 'Chargement...',
    'save': 'Enregistrer',
    'cancel': 'Annuler',
    'submit': 'Soumettre',
    'continue': 'Continuer',
    'back': 'Retour',
    'next': 'Suivant',
    'previous': 'Précédent',
    'complete': 'Terminer',
    'skip': 'Ignorer',
    
    // Navigation
    'dashboard': 'Tableau de Bord',
    'assessment': 'Évaluation',
    'services': 'Services',
    'knowledge_base': 'Base de Connaissances',
    'profile': 'Profil',
    'settings': 'Paramètres',
    'logout': 'Déconnexion',
    
    // Dashboard
    'procurement_readiness': 'Préparation aux Marchés Publics',
    'assessment_complete': 'Évaluation Terminée',
    'critical_gaps': 'Lacunes Critiques',
    'active_services': 'Services Actifs',
    'readiness_score': 'Score de Préparation',
    'overall_readiness': 'Préparation Globale',
    'recommended_next_steps': 'Prochaines Étapes Recommandées',
    'recent_activity': 'Activité Récente',
    
    // Assessment
    'business_areas': 'Domaines d\'Activité',
    'start_assessment': 'Commencer l\'Évaluation',
    'continue_assessment': 'Continuer l\'Évaluation',
    'assessment_progress': 'Progrès de l\'Évaluation',
    'tier_access': 'Accès par Niveaux',
    'evidence_required': 'Preuves Requises',
    
    // Onboarding
    'getting_started': 'Pour Commencer',
    'complete_onboarding': 'Terminer l\'Orientation',
    'skip_guide': 'Ignorer le Guide',
    'lets_begin': 'Commençons',
    
    // AI Coach
    'ai_coach': 'Coach IA',
    'ask_anything': 'Demandez-moi tout sur la préparation aux marchés...',
    'ai_thinking': 'Le Coach IA réfléchit...',
    'online_ready': 'En Ligne et Prêt à Aider',
    
    // Roles
    'client': 'Client Petite Entreprise',
    'provider': 'Fournisseur de Services',
    'navigator': 'Navigateur Numérique',
    'agency': 'Agence Locale',
    
    // Success Messages
    'assessment_completed': 'Évaluation terminée avec succès!',
    'profile_updated': 'Profil mis à jour avec succès!',
    'service_requested': 'Demande de service soumise avec succès!',
    'great_progress': 'Vous faites d\'excellents progrès!',
    'certification_ready': 'Prêt pour la Certification!',
    
    // Error Messages
    'error_occurred': 'Une erreur s\'est produite',
    'try_again': 'Veuillez réessayer',
    'connection_error': 'Erreur de connexion - vérifiez votre internet',
    'invalid_input': 'Vérifiez votre saisie et réessayez'
  }
};

// Language Provider Component
export function LanguageProvider({ children }) {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [translations_cache, setTranslationsCache] = useState(translations.en);

  useEffect(() => {
    // Load saved language preference
    const savedLanguage = localStorage.getItem('polaris_language') || 'en';
    setCurrentLanguage(savedLanguage);
    setTranslationsCache(translations[savedLanguage] || translations.en);
  }, []);

  const changeLanguage = (language) => {
    if (translations[language]) {
      setCurrentLanguage(language);
      setTranslationsCache(translations[language]);
      localStorage.setItem('polaris_language', language);
      
      // Trigger page refresh to apply translations
      window.location.reload();
    }
  };

  const translate = (key, fallback = null) => {
    return translations_cache[key] || fallback || key;
  };

  const value = {
    currentLanguage,
    changeLanguage,
    translate,
    availableLanguages: [
      { code: 'en', name: 'English', flag: '🇺🇸' },
      { code: 'es', name: 'Español', flag: '🇪🇸' },
      { code: 'fr', name: 'Français', flag: '🇫🇷' }
    ]
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

// Hook to use translations
export function useTranslation() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
}

// Language Selector Component
export function LanguageSelector() {
  const { currentLanguage, changeLanguage, availableLanguages } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 transition-colors"
      >
        <span className="text-lg">
          {availableLanguages.find(lang => lang.code === currentLanguage)?.flag || '🌐'}
        </span>
        <span className="hidden sm:inline">
          {availableLanguages.find(lang => lang.code === currentLanguage)?.name || 'English'}
        </span>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div className="absolute top-full right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border z-50">
            <div className="p-2">
              {availableLanguages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => {
                    changeLanguage(language.code);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                    currentLanguage === language.code
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span className="text-lg">{language.flag}</span>
                  <span>{language.name}</span>
                  {currentLanguage === language.code && (
                    <svg className="w-4 h-4 ml-auto text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
        </>
      )}
    </div>
  );
}

// Helper component for translated text
export function T({ children, fallback = null }) {
  const { translate } = useTranslation();
  return translate(children, fallback);
}

// Helper hook for formatted translations with variables
export function useFormattedTranslation() {
  const { translate } = useTranslation();
  
  const formatTranslation = (key, variables = {}, fallback = null) => {
    let text = translate(key, fallback);
    
    // Replace variables in format {variableName}
    Object.entries(variables).forEach(([variable, value]) => {
      const regex = new RegExp(`{${variable}}`, 'g');
      text = text.replace(regex, value);
    });
    
    return text;
  };
  
  return { formatTranslation, translate };
}