interface Announcement {
  id: number;
  title: string;
  date: string;
  category: string;
  description: string;
  priority: 'high' | 'medium' | 'normal';
}

interface Initiative {
  title: string;
  status: 'Active' | 'Ongoing' | 'Planning';
  progress: number;
  deadline: string;
  description: string;
}

export const announcements: Announcement[] = [
  {
    id: 1,
    title: "Smart City Initiative Phase 2 Launch",
    date: "2024-02-01",
    category: "Infrastructure",
    description: "The second phase of Smart City project implementation begins with focus on digital infrastructure.",
    priority: "high"
  },
  {
    id: 2,
    title: "New Citizen Services Portal",
    date: "2024-02-05",
    category: "Digital Services",
    description: "Access all government services through our new unified digital platform.",
    priority: "medium"
  },
  {
    id: 3,
    title: "Public Transportation Update",
    date: "2024-02-10",
    category: "Transport",
    description: "New bus routes and smart card system implementation starting next month.",
    priority: "normal"
  }
];

export const initiatives: Initiative[] = [
  {
    title: "Digital Literacy Program",
    status: "Active",
    progress: 75,
    deadline: "March 2024",
    description: "Training 10,000 citizens in basic digital skills"
  },
  {
    title: "Green City Initiative",
    status: "Ongoing",
    progress: 60,
    deadline: "June 2024",
    description: "Planting 100,000 trees across the city"
  },
  {
    title: "Smart Traffic Management",
    status: "Planning",
    progress: 30,
    deadline: "December 2024",
    description: "AI-powered traffic signal optimization"
  }
];
