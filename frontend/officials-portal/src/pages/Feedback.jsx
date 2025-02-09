import React, { useState } from 'react';

function Feedback() {
  const [feedbacks, setFeedbacks] = useState([
    {
      id: 1,
      grievanceId: "GR001",
      rating: 4,
      comment: "Issue was resolved quickly",
      aiSuggestion: "Similar drainage issues can be prevented with regular maintenance",
      timestamp: "2024-01-20"
    },
    {
      id: 2,
      grievanceId: "GR002",
      rating: 3,
      comment: "Resolution took longer than expected",
      aiSuggestion: "Consider implementing automated task delegation for faster response",
      timestamp: "2024-01-19"
    }
  ]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Citizen Feedback & AI Insights</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {feedbacks.map((feedback) => (
          <div key={feedback.id} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <div className="flex justify-between items-start">
              <h3 className="text-lg font-semibold">Grievance #{feedback.grievanceId}</h3>
              <div className="flex items-center">
                {[...Array(5)].map((_, index) => (
                  <span
                    key={index}
                    className={`text-xl ${
                      index < feedback.rating ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
            </div>
            
            <div className="mt-4">
              <p className="text-gray-600 dark:text-gray-300">{feedback.comment}</p>
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded">
                <h4 className="font-semibold text-blue-700 dark:text-blue-300">AI Suggestion:</h4>
                <p className="text-blue-600 dark:text-blue-200">{feedback.aiSuggestion}</p>
              </div>
              <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                Received on: {feedback.timestamp}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Feedback;
