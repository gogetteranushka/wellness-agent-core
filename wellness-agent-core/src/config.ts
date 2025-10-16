// Configuration for API endpoints and app settings

const config = {
  // API Base URL - change this when deploying to production
  API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  
  // API Endpoints
  endpoints: {
    home: '/',
    symptomCheck: '/api/symptom-check',
    dietPlan: '/api/diet-plan',
    analytics: '/api/analytics',
    explorerConditions: '/api/explorer/conditions',
    explorerConditionDetails: (condition: string) => `/api/explorer/condition/${condition}`,
  },
  
  // App settings
  app: {
    name: 'Agentic AI for Wellness',
    version: '1.0.0',
  },
  
  // Timeout for API requests (in milliseconds)
  timeout: 30000,
};

export default config;
