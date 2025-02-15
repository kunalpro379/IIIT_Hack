import React, { useState } from 'react';
import { MessageCircle, ThumbsUp, ThumbsDown, TrendingUp, BarChart2, User, Hash, BarChart } from 'lucide-react';
import { translations } from '../translations';

interface DiscussionForumProps {
  language: 'en' | 'hi';
  theme: 'light' | 'dark';
}

interface Comment {
  id: string;
  user: string;
  text: string;
  timestamp: Date;
  tags: string[];
  replies: Reply[];
  likes: number;
}

interface Reply {
  id: string;
  user: string;
  text: string;
  timestamp: Date;
}

interface Grievance {
  id: string;
  title: string;
  description: string;
  department: string;
  location: string;
  status: 'pending' | 'in-progress' | 'resolved';
  timestamp: Date;
  tags: string[];
  comments: Comment[];
}

interface DiscussionPost {
  id: string;
  title: string;
  content: string;
  author: string | 'anonymous';
  timestamp: Date;
  tags: string[];
  upvotes: number;
  downvotes: number;
  comments: Comment[];
  category: string;
  isAnonymous: boolean;
  priority?: 'high' | 'medium' | 'low';
  aiSummary?: string;
  poll?: {
    question: string;
    options: { text: string; votes: number }[];
    endDate: Date;
  };
  isVerified: boolean;
  officialResponses: {
    officialId: string;
    response: string;
    timestamp: Date;
  }[];
  reports: number;
  isFlagged: boolean;
  mentionedUsers: string[];
}

interface VerifiedOfficial {
  id: string;
  username: string;
  department: string;
  role: string;
  isOnline: boolean;
}

// Add new interfaces for priority and status tracking
interface PriorityTag {
  level: 'high' | 'medium' | 'low';
  color: string;
  icon: string;
}

// Add new interface for poll analytics
interface PollAnalytics {
  totalVotes: number;
  trendByTime: { date: Date; votes: number }[];
  demographicData?: {
    byAge: { range: string; count: number }[];
    byLocation: { area: string; count: number }[];
  };
}

// Mock UP Government departments
const departments = [
  { id: 'pwd', name: 'Public Works Department' },
  { id: 'health', name: 'Health Department' },
  { id: 'education', name: 'Education Department' },
  { id: 'police', name: 'UP Police' },
  { id: 'transport', name: 'Transport Department' }
];

// Mock grievance data
const mockGrievances: Grievance[] = [
  {
    id: '1',
    title: 'Poor Road Condition in Hazratganj',
    description: 'The road near Hazratganj market is full of potholes...',
    department: 'pwd',
    location: 'Lucknow',
    status: 'in-progress',
    timestamp: new Date('2024-01-15'),
    tags: ['infrastructure', 'roads', 'urgent'],
    comments: [
      {
        id: 'c1',
        user: 'Citizen123',
        text: 'Facing the same issue. Need immediate attention.',
        timestamp: new Date('2024-01-16'),
        tags: ['support'],
        replies: [],
        likes: 5
      }
    ]
  },
  // ...more mock grievances
];

// Add mock officials data
const mockOfficials: VerifiedOfficial[] = [
  {
    id: 'off1',
    username: 'PWD_Officer',
    department: 'Public Works',
    role: 'Chief Engineer',
    isOnline: true
  },
  {
    id: 'off2',
    username: 'Health_Director',
    department: 'Health',
    role: 'Director',
    isOnline: false
  },
  {
    id: 'off3',
    username: 'Education_Dept',
    department: 'Education',
    role: 'Secretary',
    isOnline: true
  }
];

const DiscussionForum: React.FC<DiscussionForumProps> = ({ language, theme }) => {
  const t = translations[language];
  const [activeGrievance, setActiveGrievance] = useState<Grievance | null>(null);
  const [chatVisible, setChatVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [selectedView, setSelectedView] = useState<'trending' | 'recent' | 'polls'>('trending');
  const [reportedPosts, setReportedPosts] = useState<Set<string>>(new Set());
  const [moderationQueue, setModerationQueue] = useState<string[]>([]);
  const [expandedComments, setExpandedComments] = useState<Set<string>>(new Set());
  const [userVotes, setUserVotes] = useState<Record<string, string>>({}); // Track user votes by pollId
  const [showPollAnalytics, setShowPollAnalytics] = useState<Record<string, boolean>>({});

  const categories = [
    { id: 'all', name: 'All Topics' },
    { id: 'infrastructure', name: 'Infrastructure' },
    { id: 'health', name: 'Healthcare' },
    { id: 'education', name: 'Education' },
    { id: 'sanitation', name: 'Sanitation' },
    { id: 'transport', name: 'Transport' }
  ];

  const mockDiscussions: DiscussionPost[] = [
    {
      id: '1',
      title: 'Severe Waterlogging in Indira Nagar Sector 11',
      content: 'During monsoon, the entire area gets waterlogged causing severe inconvenience...',
      author: 'Concerned_Citizen',
      timestamp: new Date('2024-01-15'),
      tags: ['#Drainage', '#Infrastructure', '#Urgent'],
      upvotes: 234,
      downvotes: 12,
      comments: [
        {
          id: 'c1',
          user: 'Municipal_Engineer',
          text: 'We have inspected the site. The drainage system requires upgrading. Work order being issued.',
          timestamp: new Date('2024-01-16'),
          tags: ['#Official'],
          replies: [
            {
              id: 'r1',
              user: 'Local_Councilor',
              text: 'Budget has been approved for this work. Expected completion: 2 weeks.',
              timestamp: new Date('2024-01-16')
            }
          ],
          likes: 45
        },
        {
          id: 'c2',
          user: 'resident_123',
          text: 'This has been an issue for 2 years now!',
          timestamp: new Date('2024-01-16'),
          tags: [],
          replies: [],
          likes: 28
        }
      ],
      category: 'infrastructure',
      isAnonymous: false,
      isVerified: true,
      priority: 'high',
      officialResponses: [],
      reports: 0,
      isFlagged: false,
      mentionedUsers: []
    },
    {
      id: '2',
      title: 'State of Roads in Gomti Nagar',
      content: 'The condition of roads has deteriorated significantly...',
      author: 'RoadSafety_Advocate',
      timestamp: new Date(),
      tags: ['#RoadRepair', '#Infrastructure', '#Safety'],
      upvotes: 45,
      downvotes: 5,
      comments: [
        {
          id: 'c1',
          user: 'PWD_Officer',
          text: 'We have initiated repair work. Expected completion in 2 weeks.',
          timestamp: new Date(),
          tags: ['#Official'],
          replies: [],
          likes: 12
        }
      ],
      category: 'infrastructure',
      isAnonymous: false,
      isVerified: true,
      officialResponses: [
        {
          officialId: 'off1',
          response: 'Work order has been issued. Construction begins Monday.',
          timestamp: new Date()
        }
      ],
      reports: 0,
      isFlagged: false,
      mentionedUsers: ['@PWD_Officer'],
      aiSummary: 'Multiple citizens reporting road damage in Gomti Nagar area. Key concerns: safety and vehicle damage.',
    },
    {
      id: '3',
      title: 'Water Supply Schedule Poll',
      content: 'What time would you prefer for water supply?',
      author: 'WaterDept_Official',
      timestamp: new Date(),
      tags: ['#WaterSupply', '#Poll'],
      upvotes: 32,
      downvotes: 2,
      comments: [],
      category: 'infrastructure',
      isAnonymous: false,
      poll: {
        question: 'Preferred water supply timing?',
        options: [
          { text: 'Morning (6-8 AM)', votes: 150 },
          { text: 'Evening (6-8 PM)', votes: 89 },
          { text: 'Both times', votes: 234 }
        ],
        endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      },
      isVerified: false,
      officialResponses: [],
      reports: 0,
      isFlagged: false,
      mentionedUsers: [],
    },
    {
      id: '4',
      title: 'Healthcare Center Proposal for Indira Nagar',
      content: 'Given the growing population in Indira Nagar, we need a new healthcare facility...',
      author: 'HealthServices_Dir',
      timestamp: new Date('2024-01-20'),
      tags: ['#Healthcare', '#Development', '#PublicHealth'],
      upvotes: 89,
      downvotes: 3,
      comments: [
        {
          id: 'c3',
          user: 'Medical_Officer',
          text: 'A survey has been conducted and location shortlisting is in progress.',
          timestamp: new Date('2024-01-21'),
          tags: ['#Official'],
          replies: [],
          likes: 34
        }
      ],
      category: 'health',
      isAnonymous: false,
      isVerified: true,
      officialResponses: [],
      reports: 0,
      isFlagged: false,
      mentionedUsers: [],
      aiSummary: 'Community requesting new healthcare facility in Indira Nagar. Population growth cited as main reason.'
    },
    {
      id: '5',
      title: 'School Infrastructure Development Plan',
      content: 'Proposing smart classrooms and computer labs in government schools...',
      author: 'Education_Secretary',
      timestamp: new Date('2024-01-18'),
      tags: ['#Education', '#SmartCity', '#DigitalLearning'],
      upvotes: 156,
      downvotes: 8,
      comments: [],
      category: 'education',
      isAnonymous: false,
      poll: {
        question: 'Which facility should be prioritized?',
        options: [
          { text: 'Computer Labs', votes: 245 },
          { text: 'Science Labs', votes: 189 },
          { text: 'Library Upgrade', votes: 167 },
          { text: 'Sports Facilities', votes: 203 }
        ],
        endDate: new Date('2024-02-01')
      },
      isVerified: true,
      officialResponses: [],
      reports: 0,
      isFlagged: false,
      mentionedUsers: []
    },
  ];

  // Add community polls data
  const communityPolls = [
    {
      id: 'poll1',
      title: 'Road Repair Priority Areas',
      question: 'Which area needs immediate road repair?',
      options: [
        { id: 'opt1', text: 'Hazratganj Market', votes: 234 },
        { id: 'opt2', text: 'Gomti Nagar Extension', votes: 189 },
        { id: 'opt3', text: 'Indira Nagar Sector 11', votes: 156 },
        { id: 'opt4', text: 'Aliganj Main Road', votes: 145 }
      ],
      totalVotes: 724,
      department: 'PWD',
      endDate: new Date('2024-02-01'),
      analytics: {
        trendByTime: [
          { date: new Date('2024-01-15'), votes: 150 },
          { date: new Date('2024-01-16'), votes: 200 },
          { date: new Date('2024-01-17'), votes: 374 }
        ],
        byLocation: [
          { area: 'North Lucknow', count: 300 },
          { area: 'South Lucknow', count: 424 }
        ]
      }
    },
    {
      id: 'poll2',
      title: 'Healthcare Facility Timing',
      question: 'What should be the optimal timing for the new healthcare center?',
      options: [
        { id: 'opt1', text: '24x7', votes: 456 },
        { id: 'opt2', text: '8 AM - 10 PM', votes: 234 },
        { id: 'opt3', text: 'Regular hours with emergency service', votes: 289 }
      ],
      totalVotes: 979,
      department: 'Health',
      endDate: new Date('2024-02-05')
    },
    // Add 3 more polls...
  ];

  const handleReport = (postId: string) => {
    if (!reportedPosts.has(postId)) {
      setReportedPosts(new Set([...reportedPosts, postId]));
      setModerationQueue([...moderationQueue, postId]);
    }
  };

  const toggleCommentExpansion = (commentId: string) => {
    const newExpanded = new Set(expandedComments);
    if (expandedComments.has(commentId)) {
      newExpanded.delete(commentId);
    } else {
      newExpanded.add(commentId);
    }
    setExpandedComments(newExpanded);
  };

  const handleVote = (pollId: string, optionId: string) => {
    if (!userVotes[pollId]) {
      setUserVotes(prev => ({ ...prev, [pollId]: optionId }));
      // Update poll results logic here
    }
  };

  const renderReplies = (replies: Reply[], commentId: string) => {
    const isExpanded = expandedComments.has(commentId);
    const displayReplies = isExpanded ? replies : replies.slice(0, 2);
    const hasMore = replies.length > 2;

    return (
      <div className="mt-2 space-y-2 relative">
        {/* Tree line */}
        <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-gray-600" />
        {displayReplies.map((reply, index) => (
          <div key={reply.id} className="pl-6 relative">
            {/* Branch line */}
            <div className="absolute left-2 top-1/2 w-3 h-0.5 bg-gray-600" />
            
            <div className={`p-2 rounded ${
              reply.user.includes('_Officer') || reply.user.includes('_Director')
                ? 'bg-blue-900/20 border border-blue-800'
                : 'bg-gray-700/30'
            }`}>
              <div className="flex items-center gap-2">
                <User className="w-3 h-3" />
                <span className={`text-sm ${
                  reply.user.includes('_Officer') || reply.user.includes('_Director')
                    ? 'font-bold text-blue-400'
                    : 'text-gray-300'
                }`}>
                  {reply.user}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(reply.timestamp).toLocaleDateString()}
                </span>
              </div>
              <p className="text-sm text-gray-300 mt-1">{reply.text}</p>
            </div>
          </div>
        ))}
        {hasMore && !isExpanded && (
          <button
            onClick={() => toggleCommentExpansion(commentId)}
            className="ml-6 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <span>Show {replies.length - 2} more replies</span>
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 011.414 1.414l-4 4a1 1 01-1.414 0l-4-4a1 1 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
        {hasMore && isExpanded && (
          <button
            onClick={() => toggleCommentExpansion(commentId)}
            className="ml-6 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <span>Show less</span>
            <svg className="w-4 h-4 transform rotate-180" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 011.414 1.414l-4 4a1 1 01-1.414 0l-4-4a1 1 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    );
  };

  const renderPollAnalytics = (poll: any) => (
    <div className="mt-4 bg-gray-700/50 p-4 rounded-lg">
      <h4 className="font-semibold text-blue-400 flex items-center gap-2">
        <BarChart className="w-4 h-4" />
        Poll Analytics
      </h4>
      
      <div className="mt-3 space-y-4">
        <div>
          <p className="text-sm text-gray-300">Total Responses: {poll.totalVotes}</p>
          <div className="h-32 mt-2">
            {/* Add a simple bar chart here */}
            <div className="flex h-full items-end space-x-2">
              {poll.options.map((option: any) => (
                <div key={option.id} className="flex-1">
                  <div 
                    className="bg-blue-600 hover:bg-blue-500 transition-all"
                    style={{ height: `${(option.votes / poll.totalVotes) * 100}%` }}
                  />
                  <p className="text-xs text-gray-400 mt-1 truncate">{option.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {poll.analytics?.trendByTime && (
          <div className="mt-4">
            <p className="text-sm text-gray-300 mb-2">Voting Trend</p>
            <div className="flex items-end space-x-1 h-24">
              {poll.analytics.trendByTime.map((point: any, index: number) => (
                <div
                  key={index}
                  className="flex-1 bg-green-600/50 hover:bg-green-500/50 transition-all"
                  style={{ height: `${(point.votes / Math.max(...poll.analytics.trendByTime.map((p: any) => p.votes))) * 100}%` }}
                  title={`${point.votes} votes on ${new Date(point.date).toLocaleDateString()}`}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderPollSection = () => (
    <div className="space-y-6">
      {communityPolls.map(poll => (
        <div key={poll.id} className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700">
          <div className="flex justify-between items-start">
            <h3 className="text-lg font-semibold text-white">{poll.title}</h3>
            <span className="text-sm text-gray-400">
              Ends: {new Date(poll.endDate).toLocaleDateString()}
            </span>
          </div>
          
          <p className="text-gray-300 mt-2 mb-4">{poll.question}</p>
          
          <div className="space-y-3">
            {poll.options.map(option => (
              <button
                key={option.id}
                onClick={() => handleVote(poll.id, option.id)}
                disabled={!!userVotes[poll.id]}
                className={`w-full p-3 rounded-lg transition-all ${
                  userVotes[poll.id] === option.id
                    ? 'bg-blue-600 text-white'
                    : userVotes[poll.id]
                    ? 'bg-gray-700 text-gray-400'
                    : 'bg-gray-700 hover:bg-gray-600 text-white'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span>{option.text}</span>
                  <span className="text-sm">
                    {Math.round((option.votes / poll.totalVotes) * 100)}%
                  </span>
                </div>
                <div className="mt-2 h-1 bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${(option.votes / poll.totalVotes) * 100}%` }}
                  />
                </div>
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowPollAnalytics(prev => ({ ...prev, [poll.id]: !prev[poll.id] }))}
            className="mt-4 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <BarChart className="w-4 h-4" />
            {showPollAnalytics[poll.id] ? 'Hide Analytics' : 'Show Analytics'}
          </button>

          {showPollAnalytics[poll.id] && renderPollAnalytics(poll)}
        </div>
      ))}
    </div>
  );

  const renderDiscussionPost = (post: DiscussionPost) => (
    <div key={post.id} className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700 hover:border-blue-600 transition-all">
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center space-x-2">
          {post.isAnonymous ? (
            <User className="w-6 h-6 text-gray-400" />
          ) : (
            <div className="flex items-center">
              <span className="font-semibold text-blue-400">@{post.author}</span>
              {post.isVerified && (
                <span className="ml-2 bg-green-500 text-xs px-2 py-1 rounded-full">Verified</span>
              )}
            </div>
          )}
          <span className="text-gray-400 text-sm">
            {new Date(post.timestamp).toLocaleDateString()}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-1 hover:bg-gray-700 rounded">
            <ThumbsUp className="w-5 h-5" />
            <span className="ml-1">{post.upvotes}</span>
          </button>
          <button className="p-1 hover:bg-gray-700 rounded">
            <ThumbsDown className="w-5 h-5" />
            <span className="ml-1">{post.downvotes}</span>
          </button>
          <button 
            onClick={() => handleReport(post.id)}
            className="p-1 hover:bg-red-700 rounded"
            title="Report post"
          >
            <span className="text-red-500">⚠️</span>
          </button>
        </div>
      </div>

      <h4 className="text-lg font-semibold mb-2">{post.title}</h4>
      <p className="text-gray-300 mb-3">{post.content}</p>

      {post.aiSummary && (
        <div className="bg-gray-700 p-3 rounded-lg mb-3">
          <p className="text-sm text-gray-300">
            <span className="font-semibold">AI Summary:</span> {post.aiSummary}
          </p>
        </div>
      )}

      {post.poll && (
        <div className="bg-gray-700 p-3 rounded-lg mb-3">
          <p className="font-semibold mb-2">{post.poll.question}</p>
          <div className="space-y-2">
            {post.poll.options.map((option, index) => (
              <div key={index} className="relative">
                <div className="bg-gray-600 h-8 rounded overflow-hidden">
                  <div
                    className="bg-blue-600 h-full"
                    style={{
                      width: `${post.poll ? (option.votes / Math.max(...post.poll.options.map(o => o.votes))) * 100 : 0}%`
                    }}
                  />
                </div>
                <span className="absolute left-2 top-1/2 transform -translate-y-1/2 text-white">
                  {option.text} ({option.votes} votes)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2 mb-3">
        {post.tags.map(tag => (
          <span key={tag} className="bg-blue-600 px-2 py-1 rounded-full text-sm">
            {tag}
          </span>
        ))}
      </div>

      <button className="flex items-center text-gray-400 hover:text-white">
        <MessageCircle className="w-5 h-5 mr-1" />
        Reply
      </button>

      {/* Enhanced comments section */}
      <div className="mt-4 space-y-3">
        {post.comments.map(comment => (
          <div key={comment.id} className="pl-4 border-l-2 border-gray-700">
            <div className={`p-3 rounded-lg ${
              comment.user.includes('_Officer') || comment.user.includes('_Engineer') || comment.user.includes('_Director')
                ? 'bg-blue-900/30 border border-blue-700'
                : 'bg-gray-700/50'
            }`}>
              <div className="flex items-center gap-2 mb-1">
                <User className="w-4 h-4" />
                <span className={`${
                  comment.user.includes('_Officer') || comment.user.includes('_Engineer') || comment.user.includes('_Director')
                    ? 'font-bold text-blue-400'
                    : 'text-gray-300'
                }`}>
                  {comment.user}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(comment.timestamp).toLocaleDateString()}
                </span>
              </div>
              <p className="text-gray-200">{comment.text}</p>
              {/* Nested Replies */}
              {comment.replies && comment.replies.length > 0 && renderReplies(comment.replies, comment.id)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="h-screen flex-1 p-4 flex flex-col">
      <div className="flex-1 grid grid-cols-12 gap-6 h-full max-h-[calc(100vh-2rem)]">
        {/* Left Sidebar - Fixed */}
        <div className="col-span-3 space-y-4 sticky top-0 h-full overflow-y-auto scrollbar-hide pb-4">
          <div className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center">
              <Hash className="w-5 h-5 mr-2" />
              Categories
            </h3>
            <div className="space-y-2">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  className={`w-full text-left p-2 rounded ${
                    selectedCategory === cat.id ? 'bg-blue-600' : 'hover:bg-gray-700'
                  } text-white`}
                  onClick={() => setSelectedCategory(cat.id)}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Trending Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {['#RoadRepair', '#WaterIssue', '#Education', '#Healthcare'].map(tag => (
                <span key={tag} className="bg-blue-600 px-3 py-1 rounded-full text-sm text-white flex items-center">
                  <Hash className="w-4 h-4 mr-1" />
                  {tag.substring(1)}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content - Scrollable */}
        <div className="col-span-6 space-y-4 h-full overflow-y-auto scrollbar-hide pb-4 scroll-smooth">
          <div className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700 sticky top-0 z-10">
            <div className="flex justify-between items-center">
              <div className="flex space-x-4">
                <button
                  className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
                    selectedView === 'trending' ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                  onClick={() => setSelectedView('trending')}
                >
                  <TrendingUp className="w-5 h-5" />
                  <span>Trending</span>
                </button>
                <button
                  className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${
                    selectedView === 'polls' ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                  onClick={() => setSelectedView('polls')}
                >
                  <BarChart2 className="w-5 h-5" />
                  <span>Polls</span>
                </button>
              </div>
              <button
                className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg flex items-center gap-2 transition-all shadow-lg"
                onClick={() => setShowCreatePost(true)}
              >
                <MessageCircle className="w-5 h-5" />
                Start Discussion
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {selectedView === 'polls' ? (
              renderPollSection()
            ) : (
              mockDiscussions
                .filter(post => selectedCategory === 'all' || post.category === selectedCategory)
                .map(post => renderDiscussionPost(post))
            )}
          </div>
        </div>

        {/* Right Sidebar - Fixed */}
        <div className="col-span-3 space-y-4 sticky top-0 h-full overflow-y-auto scrollbar-hide pb-4">
          <div className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center">
              <BarChart2 className="w-5 h-5 mr-2" />
              Community Stats
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Active Discussions</span>
                <span className="font-bold">24</span>
              </div>
              <div className="flex justify-between">
                <span>Total Contributors</span>
                <span className="font-bold">156</span>
              </div>
              <div className="flex justify-between">
                <span>Issues Resolved</span>
                <span className="font-bold">89</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-700">
            <h3 className="text-xl font-bold mb-4 text-white flex items-center">
              <User className="w-5 h-5 mr-2" />
              Active Officials
            </h3>
            <div className="space-y-2">
              {mockOfficials.map(official => (
                <div key={official.id} className="flex items-center justify-between p-2 hover:bg-gray-700 rounded">
                  <div className="flex items-center space-x-2">
                    <User className="w-5 h-5" />
                    <div>
                      <span className="text-blue-400">@{official.username}</span>
                      <p className="text-xs text-gray-400">{official.role}</p>
                    </div>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${official.isOnline ? 'bg-green-500' : 'bg-gray-500'}`} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiscussionForum;
