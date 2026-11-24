import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  OptimizationRequest,
  OptimizationResponse
} from '../models/optimization.model';

@Injectable({
  providedIn: 'root'
})
export class OptimizationService {
  private readonly apiUrl = 'http://localhost:8000/api/optimization/solve';

  constructor(private http: HttpClient) {}

  solve(request: OptimizationRequest): Observable<OptimizationResponse> {
    return this.http.post<OptimizationResponse>(this.apiUrl, request);
  }
}
