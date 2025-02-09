import { useState } from "react"
import React from "react"

function Chat() {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState("")

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (newMessage.trim()) {
      setMessages([...messages, { text: newMessage, sender: "You" }])
      setNewMessage("")
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Cross-Department Chat</h2>
      <div className="h-64 overflow-y-auto mb-4 border rounded p-2">
        {messages.map((message, index) => (
          <div key={index} className="mb-2">
            <span className="font-bold">{message.sender}: </span>
            <span>{message.text}</span>
          </div>
        ))}
      </div>
      <form onSubmit={handleSendMessage} className="flex">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          className="flex-grow px-4 py-2 border rounded-l focus:outline-none focus:ring-2 focus:ring-blue-600"
          placeholder="Type your message..."
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-r hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default Chat

