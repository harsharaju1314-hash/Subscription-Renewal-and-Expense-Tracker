import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  ExpenseSummary,
  CategorySpendingResponse,
  TrendsResponse,
  BudgetUtilization,
} from '../models/analytics.model';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private readonly baseUrl = 'http://localhost:8000/api/analytics';

  constructor(private http: HttpClient) {}

  getSummary(bypassCache: boolean = false): Observable<ExpenseSummary> {
    const params = new HttpParams().set('bypass_cache', bypassCache.toString());
    return this.http.get<ExpenseSummary>(`${this.baseUrl}/summary`, { params });
  }

  getCategorySpending(bypassCache: boolean = false): Observable<CategorySpendingResponse> {
    const params = new HttpParams().set('bypass_cache', bypassCache.toString());
    return this.http.get<CategorySpendingResponse>(`${this.baseUrl}/categories`, { params });
  }

  getTrends(months: number = 6, bypassCache: boolean = false): Observable<TrendsResponse> {
    const params = new HttpParams()
      .set('months', months.toString())
      .set('bypass_cache', bypassCache.toString());
    return this.http.get<TrendsResponse>(`${this.baseUrl}/trends`, { params });
  }

  getBudgetUtilization(): Observable<BudgetUtilization> {
    return this.http.get<BudgetUtilization>(`${this.baseUrl}/budget`);
  }
}
