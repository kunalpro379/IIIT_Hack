import React, { useState, useRef, useEffect } from "react";
import { Search, Users, Send, Phone, Video, MoreVertical } from "lucide-react";

function Chat() {
  const [activeChat, setActiveChat] = useState("department");
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Mock data
  const departments = [
    { id: 1, name: "Water Department", unread: 3 },
    { id: 2, name: "Roads & Infrastructure", unread: 0 },
    { id: 3, name: "Electricity Department", unread: 1 },
    { id: 4, name: "Sanitation", unread: 2 }
  ];

  const directMessages = [
    { id: 1, name: "District Officer", online: true },
    { id: 2, name: "Nagar Sevak", online: true },
    { id: 3, name: "Gram Panchayat", online: false }
  ];

  const mockMessages = [
    {
      id: 1,
      sender: "John Doe",
      department: "Water Department",
      message: "The water pipeline repair work has been completed.",
      timestamp: "10:30 AM",
      type: "text"
    },
    {
      id: 2,
      sender: "System",
      message: "Meeting scheduled for pipeline inspection at 2 PM",
      timestamp: "10:32 AM",
      type: "notification"
    },
    {
      id: 3,
      sender: "AI Assistant",
      message: "Summary: Discussion about water pipeline repairs and next steps for inspection.",
      timestamp: "10:35 AM",
      type: "ai-summary"
    }
  ];

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim()) {
      const message = {
        id: messages.length + 1,
        sender: "You",
        message: newMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        type: "text"
      };
      setMessages([...messages, message]);
      setNewMessage("");
    }
  };

  return (
    <div className="flex flex-col md:flex-row h-[calc(100vh-2rem)] bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Sidebar */}
      <div className="w-full md:w-80 border-r border-gray-200 dark:border-gray-700">
        <div className="p-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search conversations..."
              className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg pl-10"
            />
            <Search className="absolute left-3 top-2.5 text-gray-500 h-5 w-5" />
          </div>
        </div>

        {/* Department Chats */}
        <div className="px-4 py-2">
          <h2 className="text-sm font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider mb-2">
            Departments
          </h2>
          {departments.map((dept) => (
            <button
              key={dept.id}
              onClick={() => setActiveChat("department")}
              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-between"
            >
              <span className="flex items-center">
                <Users className="h-5 w-5 mr-2 text-gray-500" />
                {dept.name}
              </span>
              {dept.unread > 0 && (
                <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                  {dept.unread}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Direct Messages */}
        <div className="px-4 py-2">
          <h2 className="text-sm font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider mb-2">
            Direct Messages
          </h2>
          {directMessages.map((dm) => (
            <button
              key={dm.id}
              onClick={() => setActiveChat("direct")}
              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
            >
              <div className="relative">
                <span className="h-2 w-2 absolute right-0 top-0 rounded-full bg-green-500"></span>
              </div>
              {dm.name}
              <span className={`ml-2 h-2 w-2 rounded-full ${dm.online ? 'bg-green-500' : 'bg-gray-300'}`}></span>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">Water Department</h3>
            <p className="text-sm text-gray-500">12 members</p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Phone className="h-5 w-5" />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Video className="h-5 w-5" />
            </button>
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <MoreVertical className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {mockMessages.map((msg) => (
            <div key={msg.id} className={`mb-4 ${msg.type === 'notification' ? 'text-center' : ''}`}>
              {msg.type === 'notification' ? (
                <div className="bg-gray-100 dark:bg-gray-700 inline-block px-4 py-2 rounded-lg text-sm">
                  {msg.message}
                </div>
              ) : msg.type === 'ai-summary' ? (
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <div className="font-semibold text-blue-600 dark:text-blue-300 mb-1">AI Summary</div>
                  <div className="text-blue-800 dark:text-blue-200">{msg.message}</div>
                </div>
              ) : (
                <div className="flex items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-1">
                      <span className="font-semibold mr-2">{msg.sender}</span>
                      <span className="text-xs text-gray-500">{msg.timestamp}</span>
                    </div>
                    <p className="bg-gray-100 dark:bg-gray-700 inline-block px-4 py-2 rounded-lg">
                      {msg.message}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSendMessage} className="flex items-center space-x-4">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center"
            >
              <Send className="h-5 w-5 mr-2" />
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Chat;