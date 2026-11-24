export type BillingCycle = 'MONTHLY' | 'ANNUAL' | 'QUARTERLY' | 'WEEKLY';
export type SubscriptionStatus = 'ACTIVE' | 'CANCELLED' | 'EXPIRED' | 'PAUSED';

export interface Category {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  created_at: string;
}

export interface Subscription {
  id: number;
  user_id: number;
  category_id: number;
  name: string;
  description?: string;
  cost: number;
  currency: string;
  billing_cycle: BillingCycle;
  start_date: string;
  renewal_date: string;
  status: SubscriptionStatus;
  auto_renew: boolean;
  payment_method?: string;
  cancellation_url?: string;
  utility_score: number;
  is_essential: boolean;
  created_at: string;
  updated_at: string;
  category?: Category;
  monthly_equivalent_cost: number;
  annual_equivalent_cost: number;
  days_until_renewal: number;
}

export interface SubscriptionFormData {
  name: string;
  category_id: number;
  cost: number;
  currency: string;
  billing_cycle: BillingCycle;
  renewal_date: string;
  status: SubscriptionStatus;
  auto_renew: boolean;
  payment_method?: string;
  utility_score: number;
  is_essential: boolean;
  description?: string;
}

export interface RenewalNotice {
  id: number;
  name: string;
  cost: number;
  currency: string;
  billing_cycle: string;
  renewal_date: string;
  days_left: number;
  category_name: string;
  is_essential: boolean;
  status: string;
}
