export const initI18n = async () => {
    try {
      // Loading translations for each language
      const [frResponse, enResponse] = await Promise.all([
        fetch('/static/localization/_locales/fr_FR/messages.json'),
        fetch('/static/localization/_locales/en/messages.json')
      ]);
  
      const [frTranslations, enTranslations] = await Promise.all([
        frResponse.json(),
        enResponse.json()
      ]);
  
      if (typeof i18next === 'undefined') {
        throw new Error('i18next is not loaded');
      }
  
      // Preparing resources for both languages
      const resources = {
        fr: {
          translation: Object.keys(frTranslations).reduce((acc, key) => {
            acc[key] = frTranslations[key].message;
            return acc;
          }, {})
        },
        en: {
          translation: Object.keys(enTranslations).reduce((acc, key) => {
            acc[key] = enTranslations[key].message;
            return acc;
          }, {})
        }
      };
  
      // Browser language detection
      const userLanguage = navigator.language.split('-')[0]; // Recover 'fr' de 'fr-FR'
      const defaultLanguage = ['fr', 'en'].includes(userLanguage) ? userLanguage : 'en';
  
      await i18next.init({
        resources,
        lng: defaultLanguage,      // Default language based on browser language
        fallbackLng: 'en',        // Fallback language if a translation is missing
        supportedLngs: ['fr', 'en'], // Supported languages
        interpolation: {
          escapeValue: false
        },
        debug: true
      });
  
    } catch (error) {
      console.error('Error initializing i18next:', error);
      throw error;
    }
  };

export const localizeContent = () => {
  try {
      const elements = document.querySelectorAll('[data-i18n]');
      
      elements.forEach(el => {
          const key = el.getAttribute('data-i18n');
          const translation = i18next.t(key);
          if (translation) {
              el.textContent = translation;
          } else {
              console.warn(`No translation found for the key: ${key}`);
          }
      });
  } catch (error) {
      console.error('Error localizing content:', error);
  }
};