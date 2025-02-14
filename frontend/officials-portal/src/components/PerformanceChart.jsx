import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowRight } from 'lucide-react';

const PerformanceChart = ({ data, onShowMore }) => {
  return (
    <motion.div
      className="p-4 sm:p-6 rounded-xl bg-white dark:bg-dark-card border border-gray-200 
        dark:border-dark-border shadow-lg h-[350px] sm:h-[400px] w-full"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
        <h3 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-100">
          Monthly Progress
        </h3>
        <motion.button
          whileHover={{ scale: 1.05, x: 5 }}
          whileTap={{ scale: 0.95 }}
          onClick={onShowMore}
          className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 
            dark:text-primary-400 mt-2 sm:mt-0"
        >
          Show Analysis <ArrowRight size={16} />
        </motion.button>
      </div>

      {/* Responsive Chart Container */}
      <div className="w-full h-[250px] sm:h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.monthlyTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: 'none',
                borderRadius: '0.5rem',
              }}
            />
            <Legend />
            <Bar dataKey="grievances" fill="#3B82F6" name="Total Grievances" />
            <Bar dataKey="resolved" fill="#10B981" name="Resolved" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

export default PerformanceChart;
