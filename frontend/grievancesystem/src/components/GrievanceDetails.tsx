import React from 'react';
import { MapPin, Calendar, Clock, User, Phone, Mail, Building2, Star } from 'lucide-react';
import { Grievance } from '../types/grievance';
import GrievanceTimeline from './GrievanceTimeline';

interface GrievanceDetailsProps {
  grievance: Grievance;
  onClose: () => void;
}

const GrievanceDetails: React.FC<GrievanceDetailsProps> = ({ grievance, onClose }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Resolved':
        return 'bg-green-100 text-green-800';
      case 'InProgress':
        return 'bg-blue-100 text-blue-800';
      case 'UnderReview':
        return 'bg-yellow-100 text-yellow-800';
      case 'Escalated':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{grievance.title}</h2>
          <p className="text-sm text-gray-500 mt-1">ID: {grievance.id}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(grievance.status)}`}>
          {grievance.status}
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Description</h3>
            <p className="text-gray-700">{grievance.description}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Location Details</h3>
            <div className="space-y-2">
              <div className="flex items-center text-gray-600">
                <MapPin className="h-5 w-5 mr-2" />
                <span>{grievance.location.ward}, {grievance.location.tehsil}, {grievance.location.district}</span>
              </div>
              <div className="text-gray-600 ml-7">PIN: {grievance.location.pincode}</div>
            </div>
          </div>

          {grievance.assignedTo && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Assigned Official</h3>
              <div className="space-y-2">
                <div className="flex items-center text-gray-600">
                  <User className="h-5 w-5 mr-2" />
                  <span>{grievance.assignedTo.name}</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <Building2 className="h-5 w-5 mr-2" />
                  <span>{grievance.assignedTo.department}</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <Phone className="h-5 w-5 mr-2" />
                  <span>{grievance.assignedTo.contactNumber}</span>
                </div>
              </div>
            </div>
          )}

          {grievance.feedback && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Feedback</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Star className="h-5 w-5 text-yellow-400 mr-1" />
                  <span className="font-medium">{grievance.feedback.rating}/5</span>
                </div>
                <p className="text-gray-700">{grievance.feedback.comment}</p>
                <p className="text-sm text-gray-500 mt-2">
                  Submitted on {new Date(grievance.feedback.date).toLocaleDateString()}
                </p>
              </div>
            </div>
          )}
        </div>

        <div>
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Timeline</h3>
            <GrievanceTimeline timeline={grievance.timeline} />
          </div>

          {grievance.attachments.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Attachments</h3>
              <div className="grid grid-cols-2 gap-4">
                {grievance.attachments.map((attachment, index) => (
                  <div key={index} className="relative">
                    <img
                      src={attachment.url}
                      alt={attachment.name}
                      className="rounded-lg w-full h-48 object-cover"
                    />
                    <p className="text-sm text-gray-500 mt-1">{attachment.name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {grievance.aiSuggestions && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">AI Suggestions</h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                {grievance.aiSuggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 flex justify-end space-x-4">
        {grievance.status === 'Resolved' && !grievance.feedback && (
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 transition-colors">
            Provide Feedback
          </button>
        )}
        {grievance.status !== 'Resolved' && (
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-colors">
            Escalate Issue
          </button>
        )}
        <button
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default GrievanceDetails;