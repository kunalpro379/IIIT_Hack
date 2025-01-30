import React from 'react';
import { Globe2 } from 'lucide-react';

interface LanguageSelectorProps {
  language: 'en' | 'hi';
  setLanguage: (lang: 'en' | 'hi') => void;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ language, setLanguage }) => {
  return (
    <div className="flex items-center space-x-2">
      <Globe2 className="h-5 w-5" />
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as 'en' | 'hi')}
        className="bg-transparent text-white border border-white rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-white"
      >
        <option value="en" className="text-gray-900">English</option>
        <option value="hi" className="text-gray-900">हिंदी</option>
      </select>
    </div>
  );
};

export default LanguageSelector;