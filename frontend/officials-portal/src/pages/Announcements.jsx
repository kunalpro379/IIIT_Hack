import { useState } from "react"
import React from "react"

function Announcements({ userRole }) {
  const [announcements, setAnnouncements] = useState([])
  const [newAnnouncement, setNewAnnouncement] = useState("")

  const handleCreateAnnouncement = (e) => {
    e.preventDefault()
    if (newAnnouncement.trim()) {
      setAnnouncements([...announcements, { text: newAnnouncement, date: new Date() }])
      setNewAnnouncement("")
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Announcements</h2>
      {userRole === "department_head" && (
        <form onSubmit={handleCreateAnnouncement} className="mb-4">
          <textarea
            value={newAnnouncement}
            onChange={(e) => setNewAnnouncement(e.target.value)}
            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
            placeholder="Create a new announcement..."
            rows="3"
          ></textarea>
          <button
            type="submit"
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            Post Announcement
          </button>
        </form>
      )}
      <div className="space-y-4">
        {announcements.map((announcement, index) => (
          <div key={index} className="border-b pb-2">
            <p>{announcement.text}</p>
            <p className="text-sm text-gray-500 mt-1">{announcement.date.toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Announcements

