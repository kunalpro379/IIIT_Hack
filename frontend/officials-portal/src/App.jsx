import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import Dashboard from "./pages/Dashboard";
import React from "react";
import Layout from "./layout";
import GrievanceList from "./components/GrievanceList";
import AreaHeatmap from "./pages/AreaHeatmap";
import Chat from "./pages/Chat";
import Announcements from "./pages/Announcements";
import TaskManagement from './pages/TaskManagement';
import { ThemeProvider } from "./components/ThemeProvider";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState("");

  const handleLogin = (role) => {
    setIsAuthenticated(true);
    setUserRole(role);
  };

  return (
    <ThemeProvider defaultTheme="system" storageKey="app-theme">
      <BrowserRouter>
        <Routes>
          {/* Redirect to dashboard if authenticated, else show Login */}
          <Route 
            path="/" 
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />} 
          />

          {/* Protect Routes inside Layout */}
          {isAuthenticated ? (
            <Route path="/" element={<Layout userRole={userRole} />}>
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="grievances" element={<GrievanceList />} />
              <Route path="heatmap" element={<AreaHeatmap />} />
              <Route path="chat" element={<Chat />} />
              <Route path="announcements" element={<Announcements userRole={userRole} />} />
              <Route path="tasks" element={<TaskManagement />} />
            </Route>
          ) : (
            <Route path="/*" element={<Navigate to="/" replace />} />
          )}
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
