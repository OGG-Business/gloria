import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { 
  LoginRequest, 
  LoginResponse, 
  User, 
  Account, 
  Transfer, 
  CreateTransferRequest,
  ApiResponse,
  ListResponse,
  TransferFilters,
  AccountFilters,
  KYCDocument,
  Notification,
  DashboardStats,
  TransferChartData
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && originalRequest) {
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await this.refreshToken(refreshToken);
              localStorage.setItem('access_token', response.access_token);
              localStorage.setItem('refresh_token', response.refresh_token);
              
              // Retry original request
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
              }
              return this.api(originalRequest);
            } catch (refreshError) {
              // Refresh failed, redirect to login
              this.logout();
              return Promise.reject(refreshError);
            }
          } else {
            this.logout();
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.api.post<ApiResponse<LoginResponse>>('/auth/login', credentials);
    return response.data.data!;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/auth/logout');
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
  }

  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const response = await this.api.post<ApiResponse<LoginResponse>>('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data.data!;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<ApiResponse<User>>('/auth/me');
    return response.data.data!;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  async enableMFA(): Promise<{ qr_code: string; secret: string }> {
    const response = await this.api.post<ApiResponse<{ qr_code: string; secret: string }>>('/auth/mfa/enable');
    return response.data.data!;
  }

  async verifyMFA(code: string): Promise<void> {
    await this.api.post('/auth/mfa/verify', { code });
  }

  // Accounts
  async getAccounts(filters?: AccountFilters): Promise<ListResponse<Account>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, String(value));
          }
        }
      });
    }
    
    const response = await this.api.get<ApiResponse<ListResponse<Account>>>(`/accounts?${params.toString()}`);
    return response.data.data!;
  }

  async getAccount(accountId: string): Promise<Account> {
    const response = await this.api.get<ApiResponse<Account>>(`/accounts/${accountId}`);
    return response.data.data!;
  }

  async createAccount(accountData: Partial<Account>): Promise<Account> {
    const response = await this.api.post<ApiResponse<Account>>('/accounts', accountData);
    return response.data.data!;
  }

  async updateAccount(accountId: string, accountData: Partial<Account>): Promise<Account> {
    const response = await this.api.put<ApiResponse<Account>>(`/accounts/${accountId}`, accountData);
    return response.data.data!;
  }

  async getAccountActivity(accountId: string, page: number = 1, perPage: number = 20): Promise<ListResponse<any>> {
    const response = await this.api.get<ApiResponse<ListResponse<any>>>(`/accounts/${accountId}/activity?page=${page}&per_page=${perPage}`);
    return response.data.data!;
  }

  // Transfers
  async getTransfers(filters?: TransferFilters, page: number = 1, perPage: number = 20): Promise<ListResponse<Transfer>> {
    const params = new URLSearchParams({
      page: String(page),
      per_page: String(perPage)
    });
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, String(value));
          }
        }
      });
    }
    
    const response = await this.api.get<ApiResponse<ListResponse<Transfer>>>(`/transfers?${params.toString()}`);
    return response.data.data!;
  }

  async getTransfer(transferId: string): Promise<Transfer> {
    const response = await this.api.get<ApiResponse<Transfer>>(`/transfers/${transferId}`);
    return response.data.data!;
  }

  async createTransfer(transferData: CreateTransferRequest): Promise<Transfer> {
    const response = await this.api.post<ApiResponse<Transfer>>('/transfers', transferData);
    return response.data.data!;
  }

  async cancelTransfer(transferId: string, reason: string): Promise<void> {
    await this.api.post(`/transfers/${transferId}/cancel`, { reason });
  }

  async getTransferEvents(transferId: string): Promise<any[]> {
    const response = await this.api.get<ApiResponse<any[]>>(`/transfers/${transferId}/events`);
    return response.data.data!;
  }

  // KYC
  async getKYCDocuments(): Promise<KYCDocument[]> {
    const response = await this.api.get<ApiResponse<KYCDocument[]>>('/kyc/documents');
    return response.data.data!;
  }

  async uploadKYCDocument(file: File, documentType: string): Promise<KYCDocument> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    
    const response = await this.api.post<ApiResponse<KYCDocument>>('/kyc/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data!;
  }

  async deleteKYCDocument(documentId: string): Promise<void> {
    await this.api.delete(`/kyc/documents/${documentId}`);
  }

  // Notifications
  async getNotifications(page: number = 1, perPage: number = 20): Promise<ListResponse<Notification>> {
    const response = await this.api.get<ApiResponse<ListResponse<Notification>>>(`/notifications?page=${page}&per_page=${perPage}`);
    return response.data.data!;
  }

  async markNotificationAsRead(notificationId: string): Promise<void> {
    await this.api.put(`/notifications/${notificationId}/read`);
  }

  async markAllNotificationsAsRead(): Promise<void> {
    await this.api.put('/notifications/read-all');
  }

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.api.get<ApiResponse<DashboardStats>>('/dashboard/stats');
    return response.data.data!;
  }

  async getTransferChartData(period: string = '7d'): Promise<TransferChartData[]> {
    const response = await this.api.get<ApiResponse<TransferChartData[]>>(`/dashboard/transfers/chart?period=${period}`);
    return response.data.data!;
  }

  // Admin endpoints
  async getAdminStats(): Promise<any> {
    const response = await this.api.get<ApiResponse<any>>('/admin/stats');
    return response.data.data!;
  }

  async getAdminUsers(page: number = 1, perPage: number = 20): Promise<ListResponse<User>> {
    const response = await this.api.get<ApiResponse<ListResponse<User>>>(`/admin/users?page=${page}&per_page=${perPage}`);
    return response.data.data!;
  }

  async updateUserStatus(userId: string, status: string): Promise<User> {
    const response = await this.api.put<ApiResponse<User>>(`/admin/users/${userId}/status`, { status });
    return response.data.data!;
  }

  async getSystemLogs(page: number = 1, perPage: number = 20): Promise<ListResponse<any>> {
    const response = await this.api.get<ApiResponse<ListResponse<any>>>(`/admin/logs?page=${page}&per_page=${perPage}`);
    return response.data.data!;
  }

  // Utility methods
  async validateIBAN(iban: string): Promise<{ valid: boolean; bank_info?: any }> {
    const response = await this.api.post<ApiResponse<{ valid: boolean; bank_info?: any }>>('/utils/validate-iban', { iban });
    return response.data.data!;
  }

  async validateBIC(bic: string): Promise<{ valid: boolean; bank_info?: any }> {
    const response = await this.api.post<ApiResponse<{ valid: boolean; bank_info?: any }>>('/utils/validate-bic', { bic });
    return response.data.data!;
  }

  async getExchangeRate(fromCurrency: string, toCurrency: string): Promise<number> {
    const response = await this.api.get<ApiResponse<{ rate: number }>>(`/utils/exchange-rate?from=${fromCurrency}&to=${toCurrency}`);
    return response.data.data!.rate;
  }

  async getSupportedCurrencies(): Promise<string[]> {
    const response = await this.api.get<ApiResponse<string[]>>('/utils/currencies');
    return response.data.data!;
  }

  // WebSocket connection
  getWebSocketUrl(): string {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = process.env.REACT_APP_WS_URL || window.location.host;
    return `${wsProtocol}//${wsHost}/ws`;
  }
}

// Create singleton instance
const apiService = new ApiService();
export default apiService;