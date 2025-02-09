import React, { useState } from 'react';
import { translations } from '../translations';

interface DiscussionForumProps {
  language: 'en' | 'hi';
  theme: 'light' | 'dark';
}

const DiscussionForum: React.FC<DiscussionForumProps> = ({ language, theme }) => {
  const t = translations[language];
  const [comments, setComments] = useState<string[]>([]);
  const [newComment, setNewComment] = useState('');

  const handleAddComment = () => {
    setComments([...comments, newComment]);
    setNewComment('');
  };

  return (
    <div className={`bg-white ${theme === 'dark' ? 'text-gray-900' : 'text-gray-800'} p-6 rounded-lg shadow-md mb-12`}>
      <h3 className="text-lg font-semibold mb-4">{t.discussionForum}</h3>
      <div>
        <textarea
          className="w-full p-2 border border-gray-300 rounded-lg mb-4"
          rows={4}
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add your comment..."
        />
        <button
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
          onClick={handleAddComment}
        >
          Add Comment
        </button>
      </div>
      <div className="mt-4">
        {comments.map((comment, index) => (
          <div key={index} className="bg-gray-100 p-2 rounded-lg mb-2">
            {comment}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DiscussionForum;
