import React from 'react';
import { translations } from '../translations';

interface CommunityPollsProps {
  language: 'en' | 'hi';
  theme: 'light' | 'dark';
}

const CommunityPolls: React.FC<CommunityPollsProps> = ({ language, theme }) => {
  const t = translations[language];

  return (
    <div className={`bg-white ${theme === 'dark' ? 'text-gray-900' : 'text-gray-800'} p-6 rounded-lg shadow-md mb-12`}>
      <h3 className="text-lg font-semibold mb-4">{t.communityPolls}</h3>
      <div>
        <p>Poll Question: Do you support the new water supply project?</p>
        <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg mt-2">Vote Yes</button>
        <button className="bg-red-600 text-white px-4 py-2 rounded-lg mt-2 ml-2">Vote No</button>
      </div>
    </div>
  );
};

export default CommunityPolls;
