import React from 'react';

const Logo = () => {
  return (
    <div className="flex items-center gap-2">
      <img src="/up-logo.png" alt="UP Logo" className="h-8 w-8" />
      <div>
        <h1 className="text-lg font-bold text-white leading-none">P-GRS</h1>
        <p className="text-xs text-white/70">Grievance Redressal System</p>
      </div>
    </div>
  );
};

export default Logo;
