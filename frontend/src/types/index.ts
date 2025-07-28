// Common type definitions for the GovernmentGPT frontend

export type DocumentType = 'bill' | 'executive_order';

export type SearchType = 'keyword' | 'semantic' | 'hybrid' | 'conversational';

export interface Document {
  id: string;
  identifier: string;
  title: string;
  summary?: string;
  full_text?: string;
  document_type: DocumentType;
  status?: string;
  introduced_date?: string;
  last_action_date?: string;
  sponsor?: Legislator;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface Legislator {
  id: string;
  bioguide_id: string;
  full_name: string;
  party?: string;
  state?: string;
  district?: string;
  chamber: 'house' | 'senate';
}

export interface SearchFilters {
  document_type?: DocumentType;
  status?: string;
  date_from?: string;
  date_to?: string;
  sponsor?: string;
  chamber?: 'house' | 'senate';
}

export interface APIError {
  message: string;
  status: number;
  data?: any;
}