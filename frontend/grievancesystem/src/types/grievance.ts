export interface Grievance {
  id: string;
  title: string;
  description: string;
  category: string;
  status: 'Pending' | 'UnderReview' | 'InProgress' | 'Resolved' | 'Escalated';
  location: {
    district: string;
    tehsil: string;
    ward: string;
    pincode: string;
    coordinates?: {
      lat: number;
      lng: number;
    };
  };
  submittedBy?: {
    name: string;
    email: string;
    phone: string;
  };
  submissionDate: string;
  lastUpdated: string;
  assignedTo?: {
    name: string;
    department: string;
    contactNumber: string;
  };
  timeline: {
    date: string;
    status: string;
    description: string;
  }[];
  estimatedResolutionTime: number; // in days
  attachments: {
    url: string;
    type: string;
    name: string;
  }[];
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  feedback?: {
    rating: number;
    comment: string;
    date: string;
  };
  similarGrievances?: string[];
  aiSuggestions?: string[];
}

export interface GrievanceStats {
  total: number;
  resolved: number;
  pending: number;
  averageResolutionTime: number;
  satisfactionRate: number;
}