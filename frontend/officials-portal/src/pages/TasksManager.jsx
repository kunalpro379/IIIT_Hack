import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, Calendar, BarChart2, Users, Filter,
  Clock, CheckCircle2, AlertCircle
} from 'lucide-react';

const TaskManagement = () => {
  const [view, setView] = useState('board');

  const tasks = {
    todo: [
      {
        id: 1,
        title: "Water Pipeline Inspection",
        priority: "high",
        dueDate: "2024-02-25",
        assignee: {
          name: "John Doe",
          avatar: "/avatars/john.jpg"
        },
        department: "Water",
        progress: 0
      },
      // ... more tasks
    ],
    inProgress: [
      {
        id: 2,
        title: "Road Safety Assessment",
        priority: "medium",
        dueDate: "2024-02-26",
        assignee: {
          name: "Jane Smith",
          avatar: "/avatars/jane.jpg"
        },
        department: "Infrastructure",
        progress: 45
      }
    ],
    completed: [
      {
        id: 3,
        title: "Electricity Grid Maintenance",
        priority: "high",
        dueDate: "2024-02-24",
        assignee: {
          name: "Mike Johnson",
          avatar: "/avatars/mike.jpg"
        },
        department: "Electricity",
        progress: 100
      }
    ]
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg p-6 transition-colors duration-300">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Task Management
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Track and manage department tasks efficiently
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 
              text-white rounded-lg transition-colors duration-200"
          >
            <Plus size={20} />
            Create New Task
          </motion.button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-dark-card p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
                <p className="text-xl font-semibold text-gray-800 dark:text-gray-100">12</p>
              </div>
            </div>
          </div>
          {/* Similar stats cards for In Progress, Completed, and Total */}
        </div>

        {/* Filters and View Toggle */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <select className="pl-10 pr-4 py-2 bg-white dark:bg-dark-card border border-gray-200 
                dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 focus:ring-2 
                focus:ring-primary-500 appearance-none cursor-pointer">
                <option>All Departments</option>
                <option>Water</option>
                <option>Electricity</option>
                <option>Roads</option>
              </select>
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
            {/* More filters */}
          </div>
          
          <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
            <button className={`px-3 py-1.5 rounded-md transition-colors ${
              view === 'board' 
                ? 'bg-white dark:bg-dark-card text-gray-800 dark:text-gray-100' 
                : 'text-gray-600 dark:text-gray-400'
            }`}>
              Board View
            </button>
            <button className={`px-3 py-1.5 rounded-md transition-colors ${
              view === 'list' 
                ? 'bg-white dark:bg-dark-card text-gray-800 dark:text-gray-100' 
                : 'text-gray-600 dark:text-gray-400'
            }`}>
              List View
            </button>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(tasks).map(([status, taskList]) => (
          <div key={status} className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 capitalize">
                {status.replace(/([A-Z])/g, ' $1').trim()}
              </h3>
              <span className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded-lg text-sm 
                text-gray-600 dark:text-gray-400">
                {taskList.length}
              </span>
            </div>
            
            <div className="space-y-3">
              {taskList.map(task => (
                <motion.div
                  key={task.id}
                  layoutId={`task-${task.id}`}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white dark:bg-dark-card p-4 rounded-lg shadow-sm border 
                    border-gray-200 dark:border-gray-700 cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-800 dark:text-gray-100">
                      {task.title}
                    </h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      task.priority === 'high'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                    <Calendar className="w-4 h-4" />
                    <span>{task.dueDate}</span>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-600 dark:text-gray-400">Progress</span>
                      <span className="text-gray-700 dark:text-gray-300">{task.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                      <div
                        className="bg-primary-500 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <img
                        src={task.assignee.avatar}
                        alt={task.assignee.name}
                        className="w-6 h-6 rounded-full"
                      />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {task.assignee.name}
                      </span>
                    </div>
                    <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-lg 
                      text-gray-600 dark:text-gray-400">
                      {task.department}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskManagement;
