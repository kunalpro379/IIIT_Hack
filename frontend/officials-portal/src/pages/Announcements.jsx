import React, { useState } from 'react';
import { 
  Bell, Pin, Clock, Eye, Check, Image as ImageIcon, 
  FileText, Link as LinkIcon, Video, AlertTriangle, 
  Calendar, Users, Bot, Upload, Mail, MessageSquare,
  PhoneCall, Filter,
  Trash2, 
  Edit,
  User,
  LayoutGrid,
  History
} from 'lucide-react';

function Announcements({ userRole }) {
  const getTypeIcon = (type) => {
    switch(type) {
      case 'urgent':
        return <AlertTriangle className="text-red-500" />;
      case 'general':
        return <Bell className="text-blue-500" />;
      case 'event':
        return <Calendar className="text-green-500" />;
      default:
        return <Bell className="text-gray-500" />;
    }
  };

  const [announcements, setAnnouncements] = useState([
    {
      id: 1,
      title: "Emergency Road Repair Work",
      content: "Major repair work will be carried out on MG Road from 10th Feb to 15th Feb. Please use alternate routes.",
      type: "urgent",
      audience: "public",
      author: "John Doe",
      authorRole: "District Officer",
      department: "Roads & Infrastructure",
      timestamp: "2024-02-08T09:00:00",
      expiryDate: "2024-02-15T18:00:00",
      isPinned: true,
      viewCount: 156,
      acknowledgments: 45,
      distributionChannels: {
        email: true,
        webApp: true,
        sms: true
      },
      attachments: [
        { name: "road-map.pdf", type: "pdf" },
        { name: "diversion-routes.jpg", type: "image" }
      ]
    },
    {
      id: 2,
      title: "Monthly Progress Review Meeting",
      content: "All department heads are requested to attend the monthly review meeting with their progress reports.",
      type: "general",
      audience: "department",
      author: "Current User",
      authorRole: "Admin",
      department: "Administration",
      timestamp: "2024-02-07T14:30:00",
      expiryDate: "2024-02-10T17:00:00",
      isPinned: false,
      viewCount: 45,
      acknowledgments: 12,
      distributionChannels: {
        email: true,
        webApp: true,
        sms: false
      },
      attachments: [
        { name: "agenda.pdf", type: "pdf" }
      ]
    }
  ]);
  const [showNewAnnouncementForm, setShowNewAnnouncementForm] = useState(false);
  const [filters, setFilters] = useState({
    type: 'all',
    audience: 'all',
    status: 'all'
  });
  const [newAnnouncement, setNewAnnouncement] = useState({
    title: '',
    content: '',
    type: 'general',
    audience: 'public',
    expiryDate: '',
    isPinned: false,
    distributionChannels: {
      email: true,
      webApp: true,
      sms: false
    },
    attachments: []
  });

  const [activeTab, setActiveTab] = useState('announcements');

  const tabs = [
    { id: 'announcements', label: 'Announcements', icon: Bell },
    { id: 'posts', label: 'Posts', icon: FileText },
    { id: 'history', label: 'History', icon: History }
  ];

  // Announcement Types & Audiences Configuration
  const announcementTypes = [
    { id: 'urgent', label: 'Urgent', icon: AlertTriangle, color: 'text-red-500' },
    { id: 'general', label: 'General', icon: Bell, color: 'text-blue-500' },
    { id: 'event', label: 'Event', icon: Calendar, color: 'text-green-500' }
  ];

  const audienceTypes = [
    { id: 'public', label: 'Public', icon: Users, color: 'text-purple-500' },
    { id: 'department', label: 'Department Only', icon: FileText, color: 'text-blue-500' },
    { id: 'higher-authority', label: 'Higher Authority', icon: Users, color: 'text-orange-500' },
    { id: 'citizen', label: 'Citizens Only', icon: Users, color: 'text-green-500' }
  ];

  // Handle Media Upload
  const handleMediaUpload = (files) => {
    const newFiles = Array.from(files).map(file => ({
      name: file.name,
      type: file.type.split('/')[0],
      size: file.size,
      url: URL.createObjectURL(file)
    }));
    setNewAnnouncement(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...newFiles]
    }));
  };

  const handleEdit = (announcement) => {
    setNewAnnouncement(announcement);
    setShowNewAnnouncementForm(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this announcement?")) {
      setAnnouncements(prev => prev.filter(a => a.id !== id));
    }
  };

  // Create New Announcement Form
  const AnnouncementForm = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-2">Title</label>
        <input
          type="text"
          className="w-full p-2 border rounded-lg"
          value={newAnnouncement.title}
          onChange={e => setNewAnnouncement(prev => ({ ...prev, title: e.target.value }))}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Content</label>
        <textarea
          className="w-full p-2 border rounded-lg h-32"
          value={newAnnouncement.content}
          onChange={e => setNewAnnouncement(prev => ({ ...prev, content: e.target.value }))}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Type</label>
          <select
            className="w-full p-2 border rounded-lg"
            value={newAnnouncement.type}
            onChange={e => setNewAnnouncement(prev => ({ ...prev, type: e.target.value }))}
          >
            {announcementTypes.map(type => (
              <option key={type.id} value={type.id}>{type.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Audience</label>
          <select
            className="w-full p-2 border rounded-lg"
            value={newAnnouncement.audience}
            onChange={e => setNewAnnouncement(prev => ({ ...prev, audience: e.target.value }))}
          >
            {audienceTypes.map(type => (
              <option key={type.id} value={type.id}>{type.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Expiry Date</label>
        <input
          type="datetime-local"
          className="w-full p-2 border rounded-lg"
          value={newAnnouncement.expiryDate}
          onChange={e => setNewAnnouncement(prev => ({ ...prev, expiryDate: e.target.value }))}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Distribution Channels</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={newAnnouncement.distributionChannels.webApp}
              onChange={e => setNewAnnouncement(prev => ({
                ...prev,
                distributionChannels: { ...prev.distributionChannels, webApp: e.target.checked }
              }))}
            />
            <Bell className="ml-2" size={16} /> Web App
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={newAnnouncement.distributionChannels.email}
              onChange={e => setNewAnnouncement(prev => ({
                ...prev,
                distributionChannels: { ...prev.distributionChannels, email: e.target.checked }
              }))}
            />
            <Mail className="ml-2" size={16} /> Email
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={newAnnouncement.distributionChannels.sms}
              onChange={e => setNewAnnouncement(prev => ({
                ...prev,
                distributionChannels: { ...prev.distributionChannels, sms: e.target.checked }
              }))}
            />
            <MessageSquare className="ml-2" size={16} /> SMS
          </label>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Attachments</label>
        <div className="border-2 border-dashed rounded-lg p-4 text-center">
          <input
            type="file"
            multiple
            className="hidden"
            id="file-upload"
            onChange={e => handleMediaUpload(e.target.files)}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="mx-auto mb-2" />
            <span className="text-sm text-gray-600">Click to upload files</span>
          </label>
        </div>
        {/* Display uploaded files preview */}
        {newAnnouncement.attachments.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {newAnnouncement.attachments.map((file, index) => (
              <div key={index} className="flex items-center gap-2 bg-gray-100 p-2 rounded">
                <FileText size={16} />
                <span className="text-sm">{file.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={newAnnouncement.isPinned}
            onChange={e => setNewAnnouncement(prev => ({ ...prev, isPinned: e.target.checked }))}
          />
          <Pin className="ml-2" size={16} /> Pin Announcement
        </label>
      </div>
    </div>
  );

  const AnnouncementsList = () => (
    <div className="space-y-6">
      {/* Pinned Announcements */}
      {announcements.filter(a => a.isPinned).map(announcement => (
        <AnnouncementCard key={announcement.id} announcement={announcement} />
      ))}
      
      {/* Regular Announcements */}
      {announcements.filter(a => !a.isPinned).map(announcement => (
        <AnnouncementCard key={announcement.id} announcement={announcement} />
      ))}
    </div>
  );

  const AnnouncementCard = ({ announcement }) => (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border ${
      announcement.type === 'urgent' ? 'border-red-200' : 'border-gray-200'
    }`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div className="flex items-start gap-3">
            {getTypeIcon(announcement.type)}
            <div>
              <h3 className="font-semibold text-lg flex items-center gap-2">
                {announcement.title}
                {announcement.isPinned && <Pin size={16} className="text-yellow-500" />}
              </h3>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <User size={14} />
                {announcement.author} • {announcement.department}
              </p>
            </div>
          </div>
          
          {/* Actions */}
          {announcement.author === "Current User" && (
            <div className="flex items-center gap-2">
              <button 
                onClick={() => handleEdit(announcement)}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <Edit size={16} className="text-blue-500" />
              </button>
              <button 
                onClick={() => handleDelete(announcement.id)}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <Trash2 size={16} className="text-red-500" />
              </button>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="mt-4">
          <p className="text-gray-700 dark:text-gray-300">{announcement.content}</p>
          
          {/* Attachments */}
          {announcement.attachments?.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {announcement.attachments.map((file, index) => (
                <div key={index} className="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full text-sm">
                  <FileText size={14} />
                  {file.name}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Eye size={14} /> {announcement.viewCount} views
            </span>
            <span className="flex items-center gap-1">
              <Check size={14} /> {announcement.acknowledgments} acknowledged
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock size={14} />
            Expires: {new Date(announcement.expiryDate).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch(activeTab) {
      case 'announcements':
        return <AnnouncementsList />;
      case 'posts':
        return (
          <div className="space-y-6">
            {announcements
              .filter(a => a.type === 'general')
              .map(announcement => (
                <AnnouncementCard key={announcement.id} announcement={announcement} />
              ))}
          </div>
        );
      case 'history':
        return (
          <div className="space-y-6">
            {announcements
              .filter(a => a.author === "Current User")
              .map(announcement => (
                <AnnouncementCard key={announcement.id} announcement={announcement} />
              ))}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with filters */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Announcements</h1>
        <div className="flex gap-4">
          <button
            onClick={() => setShowNewAnnouncementForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Bell size={16} />
            New Announcement
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-4 border-b-2 px-1 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {renderTabContent()}

      {/* New Announcement Modal */}
      {showNewAnnouncementForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Create New Announcement</h2>
              <button
                onClick={() => setShowNewAnnouncementForm(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <AnnouncementForm />

            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowNewAnnouncementForm(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
              >
                Cancel
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Post Announcement
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Announcements;

