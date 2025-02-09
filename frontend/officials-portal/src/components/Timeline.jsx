import React from 'react';
import { motion } from 'framer-motion';
import { 
  Clock, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  User, 
  FileText,
  MessageCircle,
  Send,
  Settings,
  RefreshCw
} from 'lucide-react';

const Timeline = ({ data, onShowMore }) => {
  const timelineSteps = [
    {
      id: 1,
      title: 'Grievance Filed',
      description: 'Citizen submitted complaint regarding water supply',
      date: '2024-02-20',
      status: 'completed',
      icon: FileText,
      color: 'text-blue-500',
      dotColor: 'bg-blue-500',
      department: 'Water Department',
      assignedTo: 'John Doe'
    },
    {
      id: 2,
      title: 'Initial Assessment',
      description: 'Complaint categorized and priority assigned',
      date: '2024-02-21',
      status: 'completed',
      icon: Settings,
      color: 'text-green-500',
      dotColor: 'bg-green-500',
      department: 'Assessment Team',
      assignedTo: 'Sarah Smith'
    },
    {
      id: 3,
      title: 'Investigation',
      description: 'Field team dispatched for on-site inspection',
      date: '2024-02-22',
      status: 'in-progress',
      icon: User,
      color: 'text-yellow-500',
      dotColor: 'bg-yellow-500',
      department: 'Field Operations',
      assignedTo: 'Mike Johnson'
    },
    {
      id: 4,
      title: 'Resolution in Progress',
      description: 'Repair work scheduled',
      date: '2024-02-23',
      status: 'pending',
      icon: RefreshCw,
      color: 'text-purple-500',
      dotColor: 'bg-purple-500',
      department: 'Maintenance Team',
      assignedTo: 'Technical Team A'
    }
  ];

  return (
    <motion.div className="p-6 rounded-xl bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
          <Clock size={20} />
          Resolution Timeline
        </h2>
        <motion.button
          whileHover={{ scale: 1.05, x: 5 }}
          whileTap={{ scale: 0.95 }}
          onClick={onShowMore}
          className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
        >
          View All <ArrowRight size={16} />
        </motion.button>
      </div>

      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-[21px] top-4 h-full w-[2px] bg-gray-200 dark:bg-gray-700" />

        {/* Timeline Items */}
        <div className="space-y-8">
          {timelineSteps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative flex gap-4"
            >
              {/* Timeline Dot */}
              <div className={`w-11 h-11 rounded-full border-4 border-white dark:border-dark-card ${step.dotColor} 
                flex items-center justify-center shrink-0 z-10`}>
                <step.icon size={20} className="text-white" />
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg shadow-sm">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-gray-100">{step.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{step.description}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      step.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                      step.status === 'in-progress' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                      {step.status}
                    </span>
                  </div>

                  <div className="mt-3 flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center gap-1">
                      <User size={14} />
                      <span>{step.assignedTo}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle size={14} />
                      <span>{step.department}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock size={14} />
                      <span>{step.date}</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-2 flex gap-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="text-xs flex items-center gap-1 text-primary-600 hover:text-primary-700 dark:text-primary-400"
                  >
                    <MessageCircle size={12} />
                    Add Comment
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="text-xs flex items-center gap-1 text-primary-600 hover:text-primary-700 dark:text-primary-400"
                  >
                    <Send size={12} />
                    Forward
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default Timeline;
