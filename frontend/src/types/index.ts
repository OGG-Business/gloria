// User and Authentication Types
export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  mfa_enabled: boolean;
  role: UserRole;
  created_at: string;
  last_login?: string;
}

export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  BANK_OPERATOR = 'bank_operator'
}

export interface LoginRequest {
  username: string;
  password: string;
  mfa_code?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Account Types
export interface Account {
  id: string;
  account_number: string;
  iban: string;
  bic: string;
  holder_name: string;
  balance: number;
  currency: string;
  status: AccountStatus;
  account_type: AccountType;
  daily_limit: number;
  monthly_limit: number;
  created_at: string;
  updated_at: string;
}

export enum AccountStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  CLOSED = 'closed',
  PENDING = 'pending'
}

export enum AccountType {
  CURRENT = 'current',
  SAVINGS = 'savings',
  BUSINESS = 'business'
}

// Transfer Types
export interface Transfer {
  id: string;
  transfer_id: string;
  amount: number;
  currency: string;
  source_account_id: string;
  destination_account_id: string;
  beneficiary_name: string;
  beneficiary_iban: string;
  beneficiary_bic: string;
  description: string;
  status: TransferStatus;
  priority: TransferPriority;
  transfer_type: TransferType;
  swift_message_id?: string;
  mojaloop_transfer_id?: string;
  fees: number;
  exchange_rate?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  events: TransferEvent[];
  source_account: Account;
  destination_account: Account;
}

export enum TransferStatus {
  INITIATED = 'initiated',
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  RETURNED = 'returned'
}

export enum TransferPriority {
  NORMAL = 'normal',
  URGENT = 'urgent',
  EXPRESS = 'express'
}

export enum TransferType {
  SWIFT = 'swift',
  IBAN = 'iban',
  MOJALOOP = 'mojaloop',
  INTERNAL = 'internal'
}

export interface TransferEvent {
  id: string;
  transfer_id: string;
  event_type: string;
  status: TransferStatus;
  message: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface CreateTransferRequest {
  source_account_id: string;
  beneficiary_name: string;
  beneficiary_iban: string;
  beneficiary_bic: string;
  amount: number;
  currency: string;
  description: string;
  priority: TransferPriority;
  transfer_type: TransferType;
}

// KYC Types
export interface KYCDocument {
  id: string;
  user_id: string;
  document_type: DocumentType;
  file_name: string;
  file_size: number;
  mime_type: string;
  status: DocumentStatus;
  uploaded_at: string;
  verified_at?: string;
  verification_notes?: string;
}

export enum DocumentType {
  PASSPORT = 'passport',
  NATIONAL_ID = 'national_id',
  DRIVERS_LICENSE = 'drivers_license',
  UTILITY_BILL = 'utility_bill',
  BANK_STATEMENT = 'bank_statement',
  PROOF_OF_ADDRESS = 'proof_of_address'
}

export enum DocumentStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  EXPIRED = 'expired'
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
  pagination?: PaginationInfo;
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ListResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}

// Dashboard Types
export interface DashboardStats {
  total_transfers: number;
  total_amount: number;
  pending_transfers: number;
  completed_transfers: number;
  failed_transfers: number;
  total_accounts: number;
  total_balance: number;
  currency: string;
}

export interface TransferChartData {
  date: string;
  count: number;
  amount: number;
  currency: string;
}

// Form Types
export interface TransferFormData {
  source_account_id: string;
  beneficiary_name: string;
  beneficiary_iban: string;
  beneficiary_bic: string;
  amount: number;
  currency: string;
  description: string;
  priority: TransferPriority;
  transfer_type: TransferType;
}

export interface AccountFormData {
  account_type: AccountType;
  currency: string;
  holder_name: string;
  daily_limit: number;
  monthly_limit: number;
}

// Notification Types
export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  metadata?: Record<string, any>;
}

export enum NotificationType {
  TRANSFER_COMPLETED = 'transfer_completed',
  TRANSFER_FAILED = 'transfer_failed',
  KYC_APPROVED = 'kyc_approved',
  KYC_REJECTED = 'kyc_rejected',
  ACCOUNT_SUSPENDED = 'account_suspended',
  SECURITY_ALERT = 'security_alert'
}

// Error Types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ValidationError {
  field: string;
  message: string;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface TransferUpdateMessage {
  transfer_id: string;
  status: TransferStatus;
  event: TransferEvent;
}

// Filter and Search Types
export interface TransferFilters {
  status?: TransferStatus[];
  transfer_type?: TransferType[];
  priority?: TransferPriority[];
  currency?: string[];
  date_from?: string;
  date_to?: string;
  amount_min?: number;
  amount_max?: number;
  search?: string;
}

export interface AccountFilters {
  status?: AccountStatus[];
  account_type?: AccountType[];
  currency?: string[];
  search?: string;
}

// Settings Types
export interface UserSettings {
  language: string;
  timezone: string;
  currency: string;
  notifications: NotificationSettings;
  security: SecuritySettings;
}

export interface NotificationSettings {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  transfer_notifications: boolean;
  security_notifications: boolean;
  marketing_notifications: boolean;
}

export interface SecuritySettings {
  mfa_enabled: boolean;
  session_timeout: number;
  password_expiry_days: number;
  login_notifications: boolean;
}