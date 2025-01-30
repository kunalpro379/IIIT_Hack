import { Grievance, GrievanceStats } from '../types/grievance';

export const dummyGrievances: Grievance[] = [
  {
    id: 'GR2024030001',
    title: 'Water Supply Disruption',
    description: 'No water supply in our area for the last 3 days. This is causing severe inconvenience to residents.',
    category: 'Water Supply',
    status: 'InProgress',
    location: {
      district: 'Lucknow',
      tehsil: 'Lucknow City',
      ward: 'Gomti Nagar',
      pincode: '226010',
      coordinates: {
        lat: 26.8467,
        lng: 80.9462,
      },
    },
    submittedBy: {
      name: 'Rajesh Kumar',
      email: 'rajesh.kumar@example.com',
      phone: '9876543210',
    },
    submissionDate: '2024-03-01T10:30:00Z',
    lastUpdated: '2024-03-02T15:45:00Z',
    assignedTo: {
      name: 'Amit Singh',
      department: 'Water Works Department',
      contactNumber: '1800-123-4567',
    },
    timeline: [
      {
        date: '2024-03-01T10:30:00Z',
        status: 'Submitted',
        description: 'Grievance registered successfully',
      },
      {
        date: '2024-03-01T14:20:00Z',
        status: 'Under Review',
        description: 'Assigned to Water Works Department',
      },
      {
        date: '2024-03-02T15:45:00Z',
        status: 'In Progress',
        description: 'Team dispatched for inspection',
      },
    ],
    estimatedResolutionTime: 2,
    attachments: [
      {
        url: 'https://images.unsplash.com/photo-1583685828032-f0a8d7f54c8d',
        type: 'image/jpeg',
        name: 'water_issue.jpg',
      },
    ],
    priority: 'High',
    aiSuggestions: [
      'Check for pipeline damage in sector 7',
      'Verify water pressure at main supply point',
    ],
  },
  {
    id: 'GR2024030002',
    title: 'Street Light Malfunction',
    description: 'Multiple street lights not working in our colony, causing safety concerns during night time.',
    category: 'Electricity',
    status: 'Resolved',
    location: {
      district: 'Lucknow',
      tehsil: 'Lucknow City',
      ward: 'Indira Nagar',
      pincode: '226016',
      coordinates: {
        lat: 26.8761,
        lng: 80.9864,
      },
    },
    submissionDate: '2024-03-01T09:15:00Z',
    lastUpdated: '2024-03-02T16:30:00Z',
    assignedTo: {
      name: 'Priya Sharma',
      department: 'Electricity Department',
      contactNumber: '1800-123-4568',
    },
    timeline: [
      {
        date: '2024-03-01T09:15:00Z',
        status: 'Submitted',
        description: 'Grievance registered successfully',
      },
      {
        date: '2024-03-01T11:30:00Z',
        status: 'Under Review',
        description: 'Assigned to Electricity Department',
      },
      {
        date: '2024-03-02T14:20:00Z',
        status: 'In Progress',
        description: 'Maintenance team working on repairs',
      },
      {
        date: '2024-03-02T16:30:00Z',
        status: 'Resolved',
        description: 'All street lights repaired and functional',
      },
    ],
    estimatedResolutionTime: 1,
    attachments: [
      {
        url: 'https://images.unsplash.com/photo-1542574271-7f3b92e6c821',
        type: 'image/jpeg',
        name: 'street_lights.jpg',
      },
    ],
    priority: 'Medium',
    feedback: {
      rating: 4,
      comment: 'Quick resolution, but would appreciate better communication',
      date: '2024-03-03T10:00:00Z',
    },
  },
  {
    id: 'GR2024030003',
    title: 'Garbage Collection Issue',
    description: 'Regular garbage collection has stopped in our area for the past week. Waste is accumulating and causing health concerns.',
    category: 'Sanitation',
    status: 'UnderReview',
    location: {
      district: 'Lucknow',
      tehsil: 'Lucknow City',
      ward: 'Aliganj',
      pincode: '226024',
      coordinates: {
        lat: 26.8956,
        lng: 80.9462,
      },
    },
    submissionDate: '2024-03-02T11:20:00Z',
    lastUpdated: '2024-03-02T14:30:00Z',
    assignedTo: {
      name: 'Suresh Yadav',
      department: 'Sanitation Department',
      contactNumber: '1800-123-4569',
    },
    timeline: [
      {
        date: '2024-03-02T11:20:00Z',
        status: 'Submitted',
        description: 'Grievance registered successfully',
      },
      {
        date: '2024-03-02T14:30:00Z',
        status: 'Under Review',
        description: 'Assigned to Sanitation Department',
      },
    ],
    estimatedResolutionTime: 3,
    attachments: [
      {
        url: 'https://images.unsplash.com/photo-1605600659908-0ef719419d41',
        type: 'image/jpeg',
        name: 'garbage_issue.jpg',
      },
    ],
    priority: 'High',
    aiSuggestions: [
      'Schedule emergency pickup',
      'Review collection route optimization',
    ],
  },
];

export const grievanceStats: GrievanceStats = {
  total: 156,
  resolved: 89,
  pending: 67,
  averageResolutionTime: 3.5,
  satisfactionRate: 78,
};