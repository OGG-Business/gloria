const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('accessToken');

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry the original request
            return this.request(endpoint, options);
          }
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.accessToken);
        localStorage.setItem('refreshToken', data.refreshToken);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }

    // Clear tokens on refresh failure
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    return false;
  }

  // Auth endpoints
  async login(credentials: { usernameOrEmail: string; password: string; mfaCode?: string }) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    return this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
  }

  async getCurrentUser() {
    return this.request('/auth/profile');
  }

  // Transfer endpoints
  async getTransfers(params?: { page?: number; size?: number; status?: string }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    return this.request(`/transfers?${queryParams.toString()}`);
  }

  async createTransfer(transferData: any) {
    return this.request('/transfers', {
      method: 'POST',
      body: JSON.stringify(transferData),
    });
  }

  async getTransfer(id: string) {
    return this.request(`/transfers/${id}`);
  }

  // Account endpoints
  async getAccounts() {
    return this.request('/accounts');
  }

  async getAccount(id: string) {
    return this.request(`/accounts/${id}`);
  }

  async createAccount(accountData: any) {
    return this.request('/accounts', {
      method: 'POST',
      body: JSON.stringify(accountData),
    });
  }

  // KYC endpoints
  async submitKyc(kycData: any) {
    return this.request('/kyc/submit', {
      method: 'POST',
      body: JSON.stringify(kycData),
    });
  }

  async getKycStatus() {
    return this.request('/kyc/status');
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

// Export specific API modules
export const authApi = {
  login: apiClient.login.bind(apiClient),
  logout: apiClient.logout.bind(apiClient),
  refreshToken: apiClient.refreshToken.bind(apiClient),
  getCurrentUser: apiClient.getCurrentUser.bind(apiClient),
};

export const transferApi = {
  getTransfers: apiClient.getTransfers.bind(apiClient),
  createTransfer: apiClient.createTransfer.bind(apiClient),
  getTransfer: apiClient.getTransfer.bind(apiClient),
};

export const accountApi = {
  getAccounts: apiClient.getAccounts.bind(apiClient),
  getAccount: apiClient.getAccount.bind(apiClient),
  createAccount: apiClient.createAccount.bind(apiClient),
};

export const kycApi = {
  submitKyc: apiClient.submitKyc.bind(apiClient),
  getKycStatus: apiClient.getKycStatus.bind(apiClient),
};