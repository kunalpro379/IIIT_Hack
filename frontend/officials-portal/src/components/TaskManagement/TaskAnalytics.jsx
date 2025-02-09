import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Download, Clock, PieChart as PieChartIcon } from 'lucide-react';

const TaskAnalytics = () => {
  return (
    <div className="space-y-6">
      {/* Export Controls */}
      <div className="flex justify-end gap-4">
        <button
          onClick={() => {/* Export to Excel */}}
          className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
        >
          <Download size={16} /> Export to Excel
        </button>
        <button
          onClick={() => {/* Export to PDF */}}
          className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          <Download size={16} /> Export to PDF
        </button>
      </div>

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-dark-card rounded-lg p-6 shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Department Performance</h3>
          <div className="h-[300px]">
            {/* Add performance chart */}
          </div>
        </motion.div>

        {/* Resolution Time */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-dark-card rounded-lg p-6 shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Clock size={20} />
            Average Resolution Time
          </h3>
          <div className="h-[300px]">
            {/* Add resolution time chart */}
          </div>
        </motion.div>

        {/* Task Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-dark-card rounded-lg p-6 shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <PieChartIcon size={20} />
            Task Distribution
          </h3>
          <div className="h-[300px]">
            {/* Add task distribution pie chart */}
          </div>
        </motion.div>

        {/* Efficiency Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-dark-card rounded-lg p-6 shadow-lg"
        >
          <h3 className="text-lg font-semibold mb-4">Efficiency Metrics</h3>
          {/* Add efficiency metrics */}
        </motion.div>
      </div>
    </div>
  );
};

export default TaskAnalytics;
