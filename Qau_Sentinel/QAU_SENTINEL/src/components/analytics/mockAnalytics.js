const analyticsData = {
  overview: {
    totalIncidents: 42,
    activeCameras: 8,
    averageConfidence: 93,
    aiAccuracy: 96,
  },

  incidentTrend: [
    { day: "Mon", Fire: 2, Smoke: 1, Crowd: 4 },
    { day: "Tue", Fire: 1, Smoke: 3, Crowd: 2 },
    { day: "Wed", Fire: 4, Smoke: 2, Crowd: 5 },
    { day: "Thu", Fire: 2, Smoke: 4, Crowd: 3 },
    { day: "Fri", Fire: 3, Smoke: 2, Crowd: 4 },
    { day: "Sat", Fire: 1, Smoke: 2, Crowd: 3 },
    { day: "Sun", Fire: 2, Smoke: 1, Crowd: 2 },
  ],

  detectionDistribution: [
    { name: "Fire", value: 18 },
    { name: "Smoke", value: 13 },
    { name: "Crowd", value: 11 },
  ],

  cameraPerformance: [
    {
      id: 1,
      camera: "Camera 01",
      location: "Main Entrance",
      uptime: 99.2,
      incidents: 12,
      confidence: 96,
    },
    {
      id: 2,
      camera: "Camera 02",
      location: "Library",
      uptime: 98.4,
      incidents: 9,
      confidence: 94,
    },
    {
      id: 3,
      camera: "Camera 03",
      location: "Parking Area",
      uptime: 97.8,
      incidents: 14,
      confidence: 95,
    },
    {
      id: 4,
      camera: "Camera 04",
      location: "Admin Block",
      uptime: 99.5,
      incidents: 7,
      confidence: 97,
    },
  ],

  reports: [
    {
      id: 1,
      name: "Weekly Incident Report",
      date: "03 Jul 2026",
      type: "PDF",
    },
    {
      id: 2,
      name: "Monthly Analytics Report",
      date: "01 Jul 2026",
      type: "PDF",
    },
    {
      id: 3,
      name: "Camera Performance Report",
      date: "30 Jun 2026",
      type: "CSV",
    },
  ],
};

export default analyticsData;