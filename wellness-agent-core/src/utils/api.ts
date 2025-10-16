import config from '../config';

const API_BASE_URL = config.API_BASE_URL;

// Type definitions
interface ApiResponse<T = any> {
  [key: string]: T;
}

interface SymptomCheckRequest {
  symptoms: string[];
}

interface SymptomCheckResponse {
  symptoms: string[];
  total_severity: number;
  predicted_conditions: Array<{
    condition: string;
    probability: number;
    severity: string;
  }>;
  precautions: Array<any>;
}

interface DietPlanRequest {
  bmi: number;
  cholesterol: number;
  chronic_disease?: string;
  dietary_preference?: string;
}

interface DietPlanResponse {
  risk_condition: string;
  meal_plan: {
    breakfast: string;
    lunch: string;
    dinner: string;
    snack: string;
    calories: number;
    protein: number;
    carbohydrates: number;
    fat: number;
  };
  nutrient_advice: {
    increase?: string[];
    decrease?: string[];
  };
}

interface AnalyticsResponse {
  daily_calories: number[];
  daily_protein: number[];
  nutrient_gaps: {
    [key: string]: {
      current: number;
      target: number;
      unit: string;
    };
  };
  bmi_trend: number[];
}

/**
 * Generic fetch wrapper with error handling
 */
const apiFetch = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  try {
    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * API Service Object
 */
const api = {
  // Test connection
  testConnection: async (): Promise<ApiResponse> => {
    return apiFetch(config.endpoints.home);
  },

  // Symptom Checker
  checkSymptoms: async (symptoms: string[]): Promise<SymptomCheckResponse> => {
    return apiFetch<SymptomCheckResponse>(config.endpoints.symptomCheck, {
      method: 'POST',
      body: JSON.stringify({ symptoms }),
    });
  },

  // Get personalized diet plan
  getDietPlan: async (userData: DietPlanRequest): Promise<DietPlanResponse> => {
    return apiFetch<DietPlanResponse>(config.endpoints.dietPlan, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Get nutritional analytics
  getAnalytics: async (userId: string): Promise<AnalyticsResponse> => {
    return apiFetch<AnalyticsResponse>(config.endpoints.analytics, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  },

  // Get all conditions for explorer
  getConditions: async (): Promise<{ conditions: string[] }> => {
    return apiFetch(config.endpoints.explorerConditions);
  },

  // Get details for a specific condition
  getConditionDetails: async (condition: string): Promise<ApiResponse> => {
    return apiFetch(config.endpoints.explorerConditionDetails(condition));
  },

  // Save user profile (placeholder for future)
  saveProfile: async (profileData: any): Promise<ApiResponse> => {
    console.log('Saving profile:', profileData);
    return { success: true, message: 'Profile saved (mock)' };
  },

  // Update user data (placeholder for future)
  updateUserData: async (userId: string, userData: any): Promise<ApiResponse> => {
    console.log('Updating user data:', userId, userData);
    return { success: true, message: 'Data updated (mock)' };
  },
};

export default api;
export type {
  SymptomCheckRequest,
  SymptomCheckResponse,
  DietPlanRequest,
  DietPlanResponse,
  AnalyticsResponse,
};
