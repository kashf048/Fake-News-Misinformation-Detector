/**
 * API Service
 * Handles all backend API calls
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AnalysisRequest {
  headline: string;
  image_url?: string;
}

interface FactCheck {
  title: string;
  url: string;
  claim_reviewed: string;
  rating: string;
}

interface AnalysisResponse {
  _id: string;
  headline: string;
  image_url?: string;
  prediction: 'Fake' | 'Real' | 'Misleading';
  confidence: number;
  similarity?: number;
  explanation: string;
  fact_checks: FactCheck[];
  created_at: string;
}

interface AnalysisHistoryResponse {
  total: number;
  page: number;
  limit: number;
  items: AnalysisResponse[];
}

interface AnalyticsResponse {
  total_analyses: number;
  fake_count: number;
  real_count: number;
  misleading_count: number;
  average_confidence: number;
  predictions_by_date: Record<string, number>;
  top_headlines: string[];
}

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error);
        throw error;
      }
    );
  }

  /**
   * Analyze headline and image
   */
  async analyze(data: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      const response = await this.client.post<AnalysisResponse>('/api/analyze', data);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }

  /**
   * Get analysis history
   */
  async getHistory(
    page: number = 1,
    limit: number = 10,
    prediction?: string
  ): Promise<AnalysisHistoryResponse> {
    try {
      const params: any = { page, limit };
      if (prediction) {
        params.prediction = prediction;
      }
      
      const response = await this.client.get<AnalysisHistoryResponse>('/api/history', { params });
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }

  /**
   * Delete analysis by ID
   */
  async deleteAnalysis(id: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.client.delete(`/api/history/${id}`);
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }

  /**
   * Get analytics data
   */
  async getAnalytics(): Promise<AnalyticsResponse> {
    try {
      const response = await this.client.get<AnalyticsResponse>('/api/analytics');
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }

  /**
   * Download analysis report PDF
   */
  async downloadReport(id: string): Promise<Blob> {
    try {
      const response = await this.client.get(`/api/history/${id}/pdf`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    try {
      const response = await this.client.get('/api/health');
      return response.data;
    } catch (error) {
      this.handleError(error as AxiosError);
      throw error;
    }
  }

  /**
   * Handle API errors
   */
  private handleError(error: AxiosError): void {
    if (error.response) {
      console.error('Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Request error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
  }
}

export const apiService = new APIService();

export type {
  AnalysisRequest,
  AnalysisResponse,
  AnalysisHistoryResponse,
  AnalyticsResponse,
  FactCheck,
};
