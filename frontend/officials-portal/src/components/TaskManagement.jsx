import React from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';

const TaskManagement = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="bg-white dark:bg-dark-card rounded-xl p-6 shadow-lg"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
          Task Management
        </h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600">
          <Plus size={18} />
          <span>New Task</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Kanban-style columns */}
        <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
          <h3 className="font-medium mb-4 text-gray-700 dark:text-gray-300">To Do</h3>
          <div className="space-y-4">
            <div className="h-24 bg-white dark:bg-dark-card rounded-lg animate-pulse"></div>
            <div className="h-24 bg-white dark:bg-dark-card rounded-lg animate-pulse"></div>
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
          <h3 className="font-medium mb-4 text-gray-700 dark:text-gray-300">In Progress</h3>
          <div className="space-y-4">
            <div className="h-24 bg-white dark:bg-dark-card rounded-lg animate-pulse"></div>
            <div className="h-24 bg-white dark:bg-dark-card rounded-lg animate-pulse"></div>
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-dark-bg-secondary p-4 rounded-lg">
          <h3 className="font-medium mb-4 text-gray-700 dark:text-gray-300">Completed</h3>
          <div className="space-y-4">
            <div className="h-24 bg-white dark:bg-dark-card rounded-lg animate-pulse"></div>
            <div className="h-24 bg-white dark:bg-dark-card rounded-lg animate-pulse"></div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default TaskManagement;
