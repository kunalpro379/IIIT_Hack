import React from 'react'

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <img 
        src="/up.png" 
        alt="UP-GRS Logo" 
        className="h-10 w-10"
      />
      <div>
        <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">UP-GRS</h1>
        <p className="text-xs text-gray-500 dark:text-gray-400">Grievance Redressal System</p>
      </div>
    </div>
  )
}

export default Logo
