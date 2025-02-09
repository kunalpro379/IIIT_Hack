interface Translation {
  // Add all your translation keys here
  footerText: string;
  copyright: string;
  // ... other translation keys
}

interface Translations {
  en: Translation;
  hi: Translation;
}

export const translations: Translations = {
  en: {
    footerText: "Integrated Grievance Redressal System",
    copyright: "© 2024 Government of Uttar Pradesh",
    // ... other English translations
  },
  hi: {
    footerText: "एकीकृत शिकायत निवारण प्रणाली",
    copyright: "© 2024 उत्तर प्रदेश सरकार",
    // ... other Hindi translations
  }
};
