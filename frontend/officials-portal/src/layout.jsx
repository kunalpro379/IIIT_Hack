import { Outlet, Link, useNavigate, useLocation } from "react-router-dom"
import { 
  LayoutDashboard, 
  FileText, 
  Map, 
  MessageSquare, 
  Megaphone,
  LogOut,
  ChevronLeft,
  Menu
} from "lucide-react"
import React, { useState } from "react"
import Logo from "./components/Logo"
import ThemeToggle from './components/ThemeToggle'

function Layout({ userRole }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false)

  const isActive = (path) => location.pathname === path

  const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { path: "/grievances", label: "Grievances", icon: FileText },
    { path: "/heatmap", label: "Area Heatmap", icon: Map },
    { path: "/chat", label: "Chat", icon: MessageSquare },
    { path: "/announcements", label: "Announcements", icon: Megaphone },
    {path : "/tasks", label : "Task Management", icon : FileText}
  ]

  const handleLogout = () => {
    // Add logout logic here
    navigate('/')
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-dark-bg transition-colors duration-300">
      {/* Sidebar */}
      <div className={`${isSidebarCollapsed ? 'w-20' : 'w-64'} bg-white dark:bg-black border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out flex flex-col`}>
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          {isSidebarCollapsed ? (
            <img src="/up-logo.png" alt="UP-GRS" className="h-10 w-10 mx-auto" />
          ) : (
            <>
              <Logo />
              <ThemeToggle />
            </>
          )}
        </div>

        <nav className="flex-1 pt-4">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 py-3 px-4 text-gray-600 dark:text-gray-300 hover:bg-primary-50 dark:hover:bg-dark-bg hover:text-primary-600 dark:hover:text-primary-400 transition-colors ${
                isActive(item.path) ? "bg-primary-50 dark:bg-dark-bg text-primary-600 dark:text-primary-400 border-r-4 border-primary-600 dark:border-primary-400" : ""
              }`}
            >
              <item.icon size={20} />
              {!isSidebarCollapsed && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>

        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <button
            onClick={() => setSidebarCollapsed(!isSidebarCollapsed)}
            className="w-full flex items-center gap-2 text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 mb-4"
          >
            {isSidebarCollapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
            {!isSidebarCollapsed && <span>Collapse</span>}
          </button>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 p-2 rounded-md"
          >
            <LogOut size={20} />
            {!isSidebarCollapsed && <span>Logout</span>}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default Layout

