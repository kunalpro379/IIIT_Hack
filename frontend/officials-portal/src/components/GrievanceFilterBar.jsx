import React from 'react';
import { Filter, Calendar } from 'lucide-react';

const GrievanceFilterBar = ({ filters, setFilters }) => {
  const departments = ['All', 'Water Department', 'Electricity', 'Roads', 'Sanitation'];
  const statuses = ['All', 'Pending', 'In Progress', 'Completed'];
  const priorities = ['All', 'High', 'Medium', 'Low'];

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg p-4 shadow-md border border-gray-200 dark:border-dark-border">
      <div className="flex items-center gap-4 flex-wrap">
        {/* Filter Icon */}
        <div className="bg-blue-900/20 p-3 rounded-lg flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters</span>
        </div>

        {/* Status Filter */}
        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="text-white px-3 py-2 rounded-lg border border-gray-600 
            bg-blue-900 focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400
            hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
        >
          {statuses.map(status => (
            <option key={status} value={status} className="dark:bg-dark-bg">
              {status}
            </option>
          ))}
        </select>

        {/* Priority Filter */}
        <select
          value={filters.priority}
          onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
          className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
            bg-white dark:bg-dark-bg text-gray-700 dark:text-gray-200
            focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400
            hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
        >
          {priorities.map(priority => (
            <option key={priority} value={priority} className="dark:bg-dark-bg">
              {priority}
            </option>
          ))}
        </select>

        {/* Department Filter */}
        <select
          value={filters.department}
          onChange={(e) => setFilters({ ...filters, department: e.target.value })}
          className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
            bg-white dark:bg-dark-bg text-gray-700 dark:text-gray-200
            focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400
            hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
        >
          {departments.map(dept => (
            <option key={dept} value={dept} className="dark:bg-dark-bg">
              {dept}
            </option>
          ))}
        </select>

        {/* Date Range Filters */}
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
              bg-white dark:bg-dark-bg text-gray-700 dark:text-gray-200
              focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400
              hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
          />
          <span className="text-gray-500 dark:text-gray-400">to</span>
          <input
            type="date"
            value={filters.dateTo}
            onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 
              bg-white dark:bg-dark-bg text-gray-700 dark:text-gray-200
              focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400
              hover:border-gray-400 dark:hover:border-gray-500 transition-colors"
          />
        </div>
      </div>
    </div>
  );
};

export default GrievanceFilterBar;
