import React, { useState } from 'react';
import { Clock, MapPin, AlertCircle, CheckCircle, Search } from 'lucide-react';
import { translations } from '../translations';
import { dummyGrievances } from '../data/dummyData';
import GrievanceDetails from './GrievanceDetails';
import type { Grievance } from '../types/grievance';

interface GrievanceListProps {
  language: 'en' | 'hi';
}

const GrievanceList: React.FC<GrievanceListProps> = ({ language }) => {
  const t = translations[language];
  const [selectedGrievance, setSelectedGrievance] = useState<Grievance | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredGrievances = dummyGrievances.filter(grievance => {
    const matchesSearch = grievance.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         grievance.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || grievance.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Resolved':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'InProgress':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'UnderReview':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div>
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder={t.searchPlaceholder}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <Search className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="all">All Status</option>
          <option value="Pending">Pending</option>
          <option value="UnderReview">Under Review</option>
          <option value="InProgress">In Progress</option>
          <option value="Resolved">Resolved</option>
          <option value="Escalated">Escalated</option>
        </select>
      </div>

      {selectedGrievance ? (
        <GrievanceDetails
          grievance={selectedGrievance}
          onClose={() => setSelectedGrievance(null)}
        />
      ) : (
        <div className="space-y-4">
          {filteredGrievances.map((grievance) => (
            <div
              key={grievance.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedGrievance(grievance)}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">{grievance.title}</h3>
                  <p className="text-sm text-gray-500">ID: {grievance.id}</p>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(grievance.status)}
                  <span className="text-sm font-medium">{grievance.status}</span>
                </div>
              </div>
              <p className="text-gray-600 mb-3">{grievance.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center">
                  <MapPin className="h-4 w-4 mr-1" />
                  {grievance.location.district}, {grievance.location.tehsil}
                </div>
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  {new Date(grievance.submissionDate).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GrievanceList;