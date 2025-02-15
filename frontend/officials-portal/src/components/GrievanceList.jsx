import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, Clock, AlertCircle, Download, Send, Plus, Map, Camera,
  MessageCircle, CheckCircle, UserPlus, Upload, AlertOctagon,
  ChevronDown, ChevronUp, X
} from 'lucide-react';
import Timeline from './Timeline';
import GrievanceFilterBar from './GrievanceFilterBar';

const GrievanceList = () => {
  const [selectedGrievance, setSelectedGrievance] = useState(null);
  const [filters, setFilters] = useState({
    status: 'All',
    priority: 'All',
    department: 'All',
    dateFrom: '',
    dateTo: ''
  });
  const [expandedGrievance, setExpandedGrievance] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const [newComment, setNewComment] = useState('');

  const grievances = [
    {
      id: 1,
      title: "Water Supply Disruption",
      description: "Persistent water supply issues in Sector 15",
      status: "In Progress",
      priority: "High",
      department: "Water Department",
      dateSubmitted: "2024-02-20",
      citizenName: "Raj Kumar",
      location: "Sector 15, Lucknow",
      contactNumber: "+91 9876543210",
      attachments: ["complaint.pdf", "evidence1.jpg"],
      progress: 60,
      timeline: [
        {
          date: "2024-02-20",
          action: "Complaint Registered",
          details: "Initial complaint filed",
          by: "System"
        },
        {
          date: "2024-02-21",
          action: "Assessment Started",
          details: "Field team assigned for inspection",
          by: "John Doe"
        }
      ]
    },
    {
      id: 2,
      title: "Road Safety Hazard",
      description: "Multiple potholes causing accidents on NH-24",
      status: "Pending",
      priority: "High",
      department: "Public Works Department",
      dateSubmitted: "2024-02-19",
      citizenName: "Amit Singh",
      location: "NH-24, Near Chinhat",
      contactNumber: "+91 9876543211",
      attachments: ["road_damage.pdf", "photos.zip"],
      progress: 30,
      timeline: [
        {
          date: "2024-02-19",
          action: "Complaint Filed",
          details: "Emergency repair request submitted",
          by: "System"
        }
      ]
    },
    {
      id: 3,
      title: "Street Light Maintenance",
      description: "Several street lights not functioning in Gomti Nagar",
      status: "Completed",
      priority: "Medium",
      department: "Electricity Department",
      dateSubmitted: "2024-02-18",
      citizenName: "Priya Sharma",
      location: "Gomti Nagar, Sector C",
      contactNumber: "+91 9876543212",
      attachments: ["maintenance_request.pdf"],
      progress: 100,
      timeline: [
        {
          date: "2024-02-18",
          action: "Issue Reported",
          details: "Maintenance request logged",
          by: "System"
        },
        {
          date: "2024-02-19",
          action: "Inspection Complete",
          details: "Team verified the affected areas",
          by: "Technical Team"
        },
        {
          date: "2024-02-20",
          action: "Repairs Completed",
          details: "All street lights restored to working condition",
          by: "Maintenance Team"
        }
      ]
    },
    {
      id: 4,
      title: "Garbage Collection Issue",
      description: "Irregular waste collection in Indira Nagar",
      status: "In Progress",
      priority: "Medium",
      department: "Municipal Corporation",
      dateSubmitted: "2024-02-17",
      citizenName: "Mohammed Khan",
      location: "Indira Nagar, Block B",
      contactNumber: "+91 9876543213",
      attachments: ["waste_complaint.pdf"],
      progress: 75,
      timeline: [
        {
          date: "2024-02-17",
          action: "Complaint Received",
          details: "Service issue reported",
          by: "System"
        },
        {
          date: "2024-02-18",
          action: "Schedule Updated",
          details: "New collection schedule implemented",
          by: "Sanitation Department"
        }
      ]
    },
    {
      id: 5,
      title: "Public Park Maintenance",
      description: "Park equipment damaged and requires immediate attention",
      status: "Pending",
      priority: "Low",
      department: "Parks & Recreation",
      dateSubmitted: "2024-02-16",
      citizenName: "Sunita Verma",
      location: "Mahanagar Extension",
      contactNumber: "+91 9876543214",
      attachments: ["park_maintenance.pdf", "equipment_photos.zip"],
      progress: 15,
      timeline: [
        {
          date: "2024-02-16",
          action: "Maintenance Request",
          details: "Park equipment repair request filed",
          by: "System"
        }
      ]
    }
  ];

  // Filter grievances based on selected filters
  const filteredGrievances = useMemo(() => {
    return grievances.filter(grievance => {
      const matchesStatus = filters.status === 'All' || grievance.status === filters.status;
      const matchesPriority = filters.priority === 'All' || grievance.priority === filters.priority;
      const matchesDepartment = filters.department === 'All' || grievance.department === filters.department;
      
      const grievanceDate = new Date(grievance.dateSubmitted);
      const matchesDateRange = (!filters.dateFrom || grievanceDate >= new Date(filters.dateFrom)) &&
                              (!filters.dateTo || grievanceDate <= new Date(filters.dateTo));

      return matchesStatus && matchesPriority && matchesDepartment && matchesDateRange;
    });
  }, [grievances, filters]);

  // Calculate statistics
  const stats = useMemo(() => {
    const total = filteredGrievances.length;
    const pending = filteredGrievances.filter(g => g.status === 'Pending').length;
    const inProgress = filteredGrievances.filter(g => g.status === 'In Progress').length;
    const resolved = filteredGrievances.filter(g => g.status === 'Completed').length;

    return { total, pending, inProgress, resolved };
  }, [filteredGrievances]);

  const handleAddProgress = (grievanceId) => {
    // Add progress update logic
  };

  const handleViewPDF = (file) => {
    // PDF viewer logic
  };

  const handleMarkResolved = (id) => {
    // Implementation
  };

  const handleReassign = (id) => {
    // Implementation
  };

  const handleUploadProof = (id) => {
    // Implementation
  };

  const handleEscalate = (id) => {
    // Implementation
  };

  const handleAddComment = (id) => {
    // Implementation
  };

  // Expanded view of a grievance
  const ExpandedView = ({ grievance }) => (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      exit={{ height: 0, opacity: 0 }}
      className="mt-4 space-y-4"
    >
      {/* Complaint Summary */}
      <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
        <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">📄 Complaint Summary</h4>
        <p className="text-gray-600 dark:text-gray-400 text-sm">{grievance.fullDescription}</p>
        <div className="mt-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>Citizen Remarks:</strong> {grievance.citizenRemarks}
          </p>
        </div>
      </div>

      {/* Location Map */}
      {grievance.location && (
        <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <Map size={16} /> 📍 Location
          </h4>
          <div className="h-[200px] bg-gray-200 dark:bg-dark-bg rounded-lg">
            {/* Map component will go here */}
          </div>
        </div>
      )}

      {/* Evidence Photos */}
      {grievance.photos?.length > 0 && (
        <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
            <Camera size={16} /> 📸 Evidence Photos
          </h4>
          <div className="grid grid-cols-3 gap-4">
            {grievance.photos.map((photo, index) => (
              <img 
                key={index}
                src={photo}
                alt={`Evidence ${index + 1}`}
                className="rounded-lg w-full h-32 object-cover cursor-pointer hover:opacity-90"
              />
            ))}
          </div>
        </div>
      )}

      {/* Chat/Comments Section */}
      <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
        <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
          <MessageCircle size={16} /> 💬 Internal Discussion
        </h4>
        <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin mb-4">
          {grievance.comments?.map((comment, index) => (
            <div key={index} className="bg-white dark:bg-dark-bg p-3 rounded-lg">
              <div className="flex justify-between items-start">
                <span className="font-medium text-sm text-gray-900 dark:text-gray-100">
                  {comment.author}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {comment.timestamp}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                {comment.text}
              </p>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Add a comment..."
            className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 p-2 text-sm"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
          />
          <button
            onClick={() => handleAddComment(grievance.id)}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Send
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => handleMarkResolved(grievance.id)}
          className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
        >
          <CheckCircle size={16} /> ✔ Mark as Resolved
        </button>
        <button
          onClick={() => handleReassign(grievance.id)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <UserPlus size={16} /> 🔄 Reassign Task
        </button>
        <button
          onClick={() => handleUploadProof(grievance.id)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
        >
          <Upload size={16} /> 📎 Upload Proof
        </button>
        <button
          onClick={() => handleEscalate(grievance.id)}
          className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          <AlertOctagon size={16} /> 📧 Escalate
        </button>
      </div>
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 shadow-lg">
          <div className="text-sm text-white">Total</div>
          <div className="text-2xl font-bold text-white ">{stats.total}</div>
        </div>
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 shadow-lg">
          <div className="text-sm text-yellow-600 dark:text-yellow-400">Pending</div>
          <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-500">{stats.pending}</div>
        </div>
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 shadow-lg">
          <div className="text-sm text-blue-600 dark:text-blue-400">In Progress</div>
          <div className="text-2xl font-bold text-blue-700 dark:text-blue-500">{stats.inProgress}</div>
        </div>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 shadow-lg">
          <div className="text-sm text-green-600 dark:text-green-400">Resolved</div>
          <div className="text-2xl font-bold text-green-700 dark:text-green-500">{stats.resolved}</div>
        </div>
      </div>

      {/* Filter Bar */}
      <GrievanceFilterBar filters={filters} setFilters={setFilters} />

      {/* Grievance List and Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 relative">
        {/* Grievances List */}
        <div className="space-y-4 overflow-y-auto pr-4 scrollbar-none">
          {filteredGrievances.map((grievance) => (
            <motion.div
              key={grievance.id}
              className="bg-dark-card text-white rounded-lg p-6 shadow-lg"
              whileHover={{ scale: 1.01 }}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg text-white font-semibold text-gray-800 dark:text-gray-100">
                    {grievance.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {grievance.description}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm ${
                  grievance.priority === 'High' ? 'bg-red-100 text-red-800 dark:bg-red-900/30' : 
                  'bg-blue-100 text-blue-800 dark:bg-blue-900/30'
                }`}>
                  {grievance.priority}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-sm">
                  <p className="text-gray-500 dark:text-gray-400">Citizen</p>
                  <p className="font-medium dark:text-gray-200">{grievance.citizenName}</p>
                </div>
                <div className="text-sm">
                  <p className="text-gray-500 dark:text-gray-400">Location</p>
                  <p className="font-medium dark:text-gray-200">{grievance.location}</p>
                </div>
                <div className="text-sm">
                  <p className="text-gray-500 dark:text-gray-400">Department</p>
                  <p className="font-medium dark:text-gray-200">{grievance.department}</p>
                </div>
                <div className="text-sm">
                  <p className="text-gray-500 dark:text-gray-400">Submitted</p>
                  <p className="font-medium dark:text-gray-200">{grievance.dateSubmitted}</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600 dark:text-gray-400">Progress</span>
                  <span className="text-gray-600 dark:text-gray-400">{grievance.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-dark-bg-secondary rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${grievance.progress}%` }}
                  ></div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleViewPDF(grievance.attachments[0])}
                  className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                >
                  <Download size={16} />
                  View PDF
                </button>
                <button
                  onClick={() => setShowTimeline(true)}
                  className="flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700"
                >
                  <Clock size={16} />
                  Timeline
                </button>
                <button
                  onClick={() => handleAddProgress(grievance.id)}
                  className="flex items-center gap-2 text-sm text-green-600 hover:text-green-700"
                >
                  <Plus size={16} />
                  Add Progress
                </button>
              </div>

              {/* Expand/Collapse Button */}
              <button
                onClick={() => setExpandedGrievance(
                  expandedGrievance === grievance.id ? null : grievance.id
                )}
                className="mt-4 text-sm text-primary-600 hover:text-primary-700 flex items-center gap-2"
              >
                {expandedGrievance === grievance.id ? (
                  <>Less Details <ChevronUp size={16} /></>
                ) : (
                  <>More Details <ChevronDown size={16} /></>
                )}
              </button>

              {/* Expanded View */}
              <AnimatePresence>
                {expandedGrievance === grievance.id && (
                  <ExpandedView grievance={grievance} />
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Vertical Dotted Divider - updated style */}
        <div className="text-black lg:block absolute right-[33.33%] top-0 bottom-0 w-px">
          <div className="h-full w-full border-l-2 border-dotted border-white dark:border-gray-500 opacity-70"></div>
        </div>

        {/* Timeline Panel with no visible scrollbar */}
        <div className="lg:col-span-1 sticky top-0 overflow-y-auto scrollbar-none pl-4">
          <Timeline data={selectedGrievance?.timeline || []} />
        </div>
      </div>
    </div>
  );
};

export default GrievanceList;

