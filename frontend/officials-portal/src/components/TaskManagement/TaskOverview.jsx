import React from 'react';
import { motion } from 'framer-motion';
import { ClipboardList, AlertTriangle, Clock, Users } from 'lucide-react';
import TaskStats from './TaskStats';
import UrgentTasks from './UrgentTasks';
import AssignedOfficers from './AssignedOfficers';

const TaskOverview = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Task Statistics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="lg:col-span-2 grid grid-cols-2 gap-4"
      >
        <TaskStats />
        <div className="col-span-2">
          <UrgentTasks />
        </div>
      </motion.div>

      {/* Officer Workload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <AssignedOfficers />
      </motion.div>
    </div>
  );
};

export default TaskOverview;
