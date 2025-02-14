import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import Dashboard from "./pages/Dashboard";
import React from "react";
import Layout from "./Layout"; // Fixed import path
import GrievanceList from "./components/GrievanceList";
import AreaHeatmap from "./pages/AreaHeatmap";
import Chat from "./pages/Chat";
import Announcements from "./pages/Announcements";
import { ThemeProvider } from "./components/ThemeProvider";
import TaskManagement from './pages/TaskManagement';
import Feedback from "./pages/Feedback";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState("");
  const [userData, setUserData] = useState(null);

  const handleLogin = (role, data) => {
    setIsAuthenticated(true);
    setUserRole(role);
    setUserData(data);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUserRole("");
    setUserData(null);
  };

  return (
    <ThemeProvider defaultTheme="light">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/" 
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />} 
          />

          {isAuthenticated ? (
            <Route element={<Layout userRole={userRole} onLogout={handleLogout} />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard userAuth={userData} />} />
              <Route path="/grievances" element={<GrievanceList />} />
              <Route path="/heatmap" element={<AreaHeatmap />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/announcements" element={<Announcements userRole={userRole} />} />
              <Route path="/tasks" element={<TaskManagement />} />
              <Route path="/feedback" element={<Feedback />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
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