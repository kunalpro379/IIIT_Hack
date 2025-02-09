import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Clock, AlertTriangle, ArrowUpCircle } from 'lucide-react';

const TaskStats = () => {
  const stats = [
    {
      title: 'Total Tasks',
      value: '248',
      change: '+12%',
      icon: Clock,
      color: 'text-blue-500',
      bg: 'bg-blue-50 dark:bg-blue-900/20'
    },
    {
      title: 'Completed',
      value: '156',
      change: '+8%',
      icon: CheckCircle,
      color: 'text-green-500',
      bg: 'bg-green-50 dark:bg-green-900/20'
    },
    {
      title: 'In Progress',
      value: '64',
      change: '-5%',
      icon: ArrowUpCircle,
      color: 'text-yellow-500',
      bg: 'bg-yellow-50 dark:bg-yellow-900/20'
    },
    {
      title: 'Escalated',
      value: '28',
      change: '+2%',
      icon: AlertTriangle,
      color: 'text-red-500',
      bg: 'bg-red-50 dark:bg-red-900/20'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <motion.div
          key={stat.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`${stat.bg} p-6 rounded-lg`}
        >
          <div className="flex items-center justify-between">
            <stat.icon className={`h-6 w-6 ${stat.color}`} />
            <span className={`text-sm font-medium ${
              stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
            }`}>
              {stat.change}
            </span>
          </div>
          <h3 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
            {stat.value}
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {stat.title}
          </p>
        </motion.div>
      ))}
    </div>
  );
};

export default TaskStats;
