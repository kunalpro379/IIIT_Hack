import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Bell, UserCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';
import GrievanceStats from '../components/GrievanceStats';
import DepartmentPerformance from '../components/DepartmentPerformance';
import CriticalAlerts from '../components/CriticalAlerts';
import TaskAssignments from '../components/TaskAssignments';
import NotificationPanel from '../components/NotificationPanel';
import dashboardData from '../data/dashboardData';
import PerformanceChart from '../components/PerformanceChart';
import ComparativeMetrics from '../components/ComparativeMetrics';

const Dashboard = ({ userAuth }) => {
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1
    }
  };

  const handleShowAnalysis = () => navigate('/analysis');
  const handleShowAlerts = () => navigate('/alerts');
  const handleShowTimeline = () => navigate('/timeline');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg transition-colors duration-300">
      {/* Header */}
      <div className="bg-white/90 dark:bg-dark-card/90 backdrop-blur-sm rounded-lg shadow-lg p-4 mb-6 flex justify-between items-center border border-gray-200 dark:border-dark-border">
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search grievances, departments, or locations..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg dark:bg-dark-bg dark:border-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="relative"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="h-6 w-6 text-gray-600 dark:text-gray-300" />
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
              2
            </span>
          </motion.button>
          
          <motion.div
            whileHover={{ scale: 1.1 }}
            className="flex items-center gap-2 cursor-pointer"
          >
            <UserCircle className="h-6 w-6 text-gray-600 dark:text-gray-300" />
            <span className="text-sm font-medium dark:text-gray-200">{userAuth?.name || 'Admin'}</span>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {/* Stats Overview */}
          <motion.div 
            variants={itemVariants} 
            className="col-span-full bg-white dark:bg-dark-card rounded-lg shadow-md p-6 border border-gray-200 dark:border-dark-border transition-all duration-300"
          >
            <GrievanceStats data={dashboardData.overallStats} />
          </motion.div>

          {/* Performance Chart */}
          <motion.div 
            variants={itemVariants} 
            className="lg:col-span-2 bg-white dark:bg-dark-card rounded-lg shadow-md p-6 border border-gray-200 dark:border-dark-border hover:shadow-lg transition-all duration-300"
          >
            <PerformanceChart 
              data={dashboardData.overallStats} 
              onShowMore={handleShowAnalysis}
            />
          </motion.div>
          {/* Comparative Metrics */}
          <motion.div variants={itemVariants} className="lg:col-span-2 bg-white dark:bg-dark-card rounded-lg shadow-md p-6 dark:text-gray-100">
            <ComparativeMetrics data={dashboardData.comparativeAnalytics} />
          </motion.div>

          {/* Critical Alerts */}
          <motion.div variants={itemVariants} className="bg-white dark:bg-dark-card rounded-lg shadow-md p-6 dark:text-gray-100">
            <CriticalAlerts 
              alerts={dashboardData.criticalAlerts}
              onShowMore={handleShowAlerts}
            />
          </motion.div>

          {/* Task Assignments */}
          <motion.div variants={itemVariants} className="col-span-full bg-white dark:bg-dark-card rounded-lg shadow-md p-6 dark:text-gray-100">
            <TaskAssignments tasks={dashboardData.tasks} />
          </motion.div>
        </motion.div>
      </div>

      {/* Notification Panel */}
      {showNotifications && (
        <NotificationPanel
          notifications={dashboardData.recentNotifications}
          onClose={() => setShowNotifications(false)}
          className="dark:bg-gray-800 dark:text-gray-100"
        />
      )}
    </div>
  );
};

export default Dashboard;

