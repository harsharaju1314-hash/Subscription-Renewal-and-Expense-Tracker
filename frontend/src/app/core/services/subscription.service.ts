import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Subscription,
  SubscriptionFormData,
  Category,
  RenewalNotice,
  SubscriptionStatus,
} from '../models/subscription.model';

@Injectable({
  providedIn: 'root'
})
export class SubscriptionService {
  private readonly baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  getSubscriptions(filter?: {
    status?: SubscriptionStatus;
    category_id?: number;
    search?: string;
    sort_by?: string;
    order?: 'asc' | 'desc';
  }): Observable<Subscription[]> {
    let params = new HttpParams();
    if (filter?.status) params = params.set('status', filter.status);
    if (filter?.category_id) params = params.set('category_id', filter.category_id.toString());
    if (filter?.search) params = params.set('search', filter.search);
    if (filter?.sort_by) params = params.set('sort_by', filter.sort_by);
    if (filter?.order) params = params.set('order', filter.order);

    return this.http.get<Subscription[]>(`${this.baseUrl}/subscriptions`, { params });
  }

  getSubscriptionById(id: number): Observable<Subscription> {
    return this.http.get<Subscription>(`${this.baseUrl}/subscriptions/${id}`);
  }

  createSubscription(subData: SubscriptionFormData): Observable<Subscription> {
    return this.http.post<Subscription>(`${this.baseUrl}/subscriptions`, subData);
  }

  updateSubscription(id: number, subData: Partial<SubscriptionFormData>): Observable<Subscription> {
    return this.http.put<Subscription>(`${this.baseUrl}/subscriptions/${id}`, subData);
  }

  deleteSubscription(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/subscriptions/${id}`);
  }

  getUpcomingRenewals(days: number = 30): Observable<RenewalNotice[]> {
    const params = new HttpParams().set('days', days.toString());
    return this.http.get<RenewalNotice[]>(`${this.baseUrl}/subscriptions/renewals`, { params });
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.baseUrl}/categories`);
  }
}
