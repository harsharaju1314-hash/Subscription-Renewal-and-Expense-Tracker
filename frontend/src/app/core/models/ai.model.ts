export interface SourceReference {
  id: number;
  name: string;
  cost: number;
  billing_cycle: string;
  category: string;
  renewal_date?: string;
  relevance_score?: number;
}

export interface ChatMessage {
  id?: string;
  sender: 'user' | 'assistant';
  text: string;
  sources?: SourceReference[];
  latency_ms?: number;
  timestamp: Date;
  model?: string;
}

export interface AIChatResponse {
  answer: string;
  conversation_id?: number;
  sources: SourceReference[];
  latency_ms: number;
  tokens_used: number;
  model: string;
  timestamp: string;
}
