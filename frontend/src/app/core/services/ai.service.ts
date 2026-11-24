import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AIChatResponse } from '../models/ai.model';

@Injectable({
  providedIn: 'root'
})
export class AIService {
  private readonly baseUrl = 'http://localhost:8000/api/ai';

  constructor(private http: HttpClient) {}

  chat(query: string, conversationId?: number): Observable<AIChatResponse> {
    return this.http.post<AIChatResponse>(`${this.baseUrl}/chat`, {
      query,
      conversation_id: conversationId,
    });
  }

  getHistory(limit: number = 20): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/history?limit=${limit}`);
  }
}
