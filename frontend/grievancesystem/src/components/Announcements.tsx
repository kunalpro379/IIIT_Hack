import React from 'react';
import { Megaphone, Bell } from 'lucide-react';
import { announcements, initiatives } from '../data/announcements';

interface AnnouncementsProps {
  language: 'en' | 'hi';
  theme: 'light' | 'dark';
}

const Announcements: React.FC<AnnouncementsProps> = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 rounded-2xl p-8">
        <h1 className="text-3xl font-bold text-white mb-4">Public Announcements & Initiatives</h1>
        <p className="text-gray-300">Stay updated with the latest government announcements and ongoing initiatives</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Latest Announcements */}
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
              <Megaphone className="w-6 h-6 text-purple-400" />
              Latest Announcements
            </h2>
          </div>
          {announcements.map((announcement) => (
            <div 
              key={announcement.id}
              className="group p-6 rounded-xl bg-gray-800/50 border border-gray-700 hover:border-purple-500/50 transition-all duration-300"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-medium text-white group-hover:text-purple-400 transition-colors">
                  {announcement.title}
                </h3>
                <span className={`px-3 py-1 rounded-full text-xs ${
                  announcement.priority === 'high' 
                    ? 'bg-red-500/20 text-red-400'
                    : announcement.priority === 'medium'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-blue-500/20 text-blue-400'
                }`}>
                  {announcement.priority}
                </span>
              </div>
              <p className="text-gray-400 mb-4">{announcement.description}</p>
              <div className="flex justify-between items-center text-sm">
                <span className="text-purple-400">{announcement.category}</span>
                <span className="text-gray-500">{announcement.date}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Government Initiatives */}
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
              <Bell className="w-6 h-6 text-purple-400" />
              Active Initiatives
            </h2>
          </div>
          {initiatives.map((initiative, index) => (
            <div 
              key={index}
              className="p-6 rounded-xl bg-gray-800/50 border border-gray-700 hover:border-purple-500/50 transition-all duration-300"
            >
              <h3 className="text-lg font-medium text-white mb-2">{initiative.title}</h3>
              <p className="text-gray-400 mb-4">{initiative.description}</p>
              <div className="space-y-3">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${initiative.progress}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-purple-400">{initiative.status}</span>
                  <span className="text-gray-500">Deadline: {initiative.deadline}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Announcements;
