import React, { useState } from 'react';
import { Star } from 'lucide-react'; // Import Star icon from lucide-react

interface FeedbackFormProps {
  grievanceId: string;
  onSubmit: (rating: number, comments: string) => void;
  onClose: () => void;
}

const FeedbackForm: React.FC<FeedbackFormProps> = ({ grievanceId, onSubmit, onClose }) => {
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(rating, comments);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
        <h2 className="text-2xl font-bold mb-4">Rate the Resolution</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Rating</label>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className={`h-8 w-8 ${rating >= star ? 'text-yellow-500' : 'text-gray-300'}`}
                  onClick={() => setRating(star)}
                >
                  <Star />
                </button>
              ))}
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Comments</label>
            <textarea
              className="w-full p-2 border border-gray-300 rounded-lg"
              rows={4}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
            >
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackForm;
