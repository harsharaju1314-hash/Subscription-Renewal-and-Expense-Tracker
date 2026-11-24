import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { AIService } from '../../core/services/ai.service';
import { ChatMessage, SourceReference } from '../../core/models/ai.model';
import { NavbarComponent } from '../../shared/navbar/navbar.component';

@Component({
  selector: 'app-ai-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  template: `
    <div class="ai-layout">
      <app-navbar title="AI Financial Copilot"></app-navbar>

      <main class="chat-container">
        <!-- AI Intelligence Header Banner -->
        <div class="model-info-banner">
          <div class="model-left">
            <span class="material-icons bot-icon">psychology</span>
            <div>
              <strong>RAG Financial Copilot &bull; LangChain + FAISS</strong>
              <p>Strictly grounded in your authenticated MySQL subscriptions. Zero hallucinations.</p>
            </div>
          </div>
          <button class="clear-btn" (click)="clearHistory()" title="Clear Chat History">
            <span class="material-icons">restart_alt</span>
            <span>Reset</span>
          </button>
        </div>

        <!-- Chat Stream -->
        <div class="messages-stream" #scrollContainer>
          <div class="message-bubble assistant-bubble intro-message">
            <div class="bubble-header">
              <span class="bot-label">SubTrack AI Copilot</span>
              <span class="timestamp">Ready</span>
            </div>
            <p>
              Hello! I am your AI Financial Copilot. I analyze your subscriptions, renewals, and expenses using Retrieval-Augmented Generation (RAG).
            </p>
            <p class="try-prompt-hint">Click any question below to test:</p>
            <div class="quick-chips">
              <button class="chip" (click)="sendQuery('How much am I spending every month?')">
                "How much am I spending every month?"
              </button>
              <button class="chip" (click)="sendQuery('Which subscriptions cost me the most?')">
                "Which subscriptions cost me the most?"
              </button>
              <button class="chip" (click)="sendQuery('What subscriptions renew next week?')">
                "What subscriptions renew next week?"
              </button>
              <button class="chip" (click)="sendQuery('How can I reduce my monthly expenses?')">
                "How can I reduce my monthly expenses?"
              </button>
              <button class="chip" (click)="sendQuery('Compare my entertainment and streaming subscriptions.')">
                "Compare my entertainment subscriptions."
              </button>
            </div>
          </div>

          <div
            *ngFor="let msg of messages"
            class="message-row"
            [class.user-row]="msg.sender === 'user'"
            [class.assistant-row]="msg.sender === 'assistant'">

            <div class="avatar" [class.user-avatar]="msg.sender === 'user'">
              <span class="material-icons">{{ msg.sender === 'user' ? 'person' : 'smart_toy' }}</span>
            </div>

            <div class="message-bubble" [class.user-bubble]="msg.sender === 'user'" [class.assistant-bubble]="msg.sender === 'assistant'">
              <div class="bubble-header">
                <span class="sender-name">{{ msg.sender === 'user' ? 'You' : 'SubTrack AI' }}</span>
                <span class="timestamp" *ngIf="msg.latency_ms">{{ msg.latency_ms }}ms latency</span>
              </div>

              <!-- Message Content -->
              <div class="bubble-text" [innerHTML]="formatMessage(msg.text)"></div>

              <!-- Grounded Supporting References / Sources -->
              <div class="sources-wrap" *ngIf="msg.sources && msg.sources.length > 0">
                <div class="sources-header">
                  <span class="material-icons source-icon">verified</span>
                  <span>Grounded in {{ msg.sources.length }} retrieved subscription document(s):</span>
                </div>
                <div class="source-cards-grid">
                  <div class="source-card" *ngFor="let src of msg.sources">
                    <div class="src-top">
                      <strong>{{ src.name }}</strong>
                      <span class="src-cost">\${{ src.cost.toFixed(2) }}</span>
                    </div>
                    <div class="src-bottom">
                      <span>{{ src.category }} &bull; {{ src.billing_cycle }}</span>
                      <span *ngIf="src.renewal_date">Renews: {{ src.renewal_date }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div class="typing-indicator" *ngIf="loading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="typing-text">Retrieving embeddings from FAISS & synthesizing response...</span>
          </div>
        </div>

        <!-- Input Bar -->
        <div class="input-container">
          <form (ngSubmit)="onSubmit()" class="chat-form">
            <input
              type="text"
              [(ngModel)]="userInput"
              name="chatQuery"
              placeholder="Ask about spending totals, cost cuts, or renewal dates..."
              class="chat-input"
              [disabled]="loading"
            />
            <button type="submit" class="btn-primary send-btn" [disabled]="!userInput.trim() || loading">
              <span class="material-icons">send</span>
            </button>
          </form>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .ai-layout {
      margin-left: 260px;
      min-height: 100vh;
      background: #f8fafc;
      display: flex;
      flex-direction: column;
    }
    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: calc(100vh - 68px);
      max-width: 1000px;
      width: 100%;
      margin: 0 auto;
      padding: 24px;
      gap: 16px;
    }
    .model-info-banner {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .model-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .bot-icon {
      color: #6366f1;
      font-size: 28px;
    }
    .model-left strong {
      font-size: 0.92rem;
      color: #0f172a;
    }
    .model-left p {
      font-size: 0.78rem;
      color: #64748b;
    }
    .clear-btn {
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .clear-btn:hover {
      background: #e2e8f0;
    }

    .messages-stream {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding-right: 8px;
    }
    .message-row {
      display: flex;
      gap: 12px;
      align-items: flex-start;
    }
    .user-row {
      flex-direction: row-reverse;
    }
    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #eef2ff;
      color: #4f46e5;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .user-avatar {
      background: #0f172a;
      color: #ffffff;
    }
    .message-bubble {
      max-width: 80%;
      border-radius: 14px;
      padding: 16px 20px;
      font-size: 0.92rem;
      line-height: 1.5;
    }
    .assistant-bubble {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      color: #1e293b;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .user-bubble {
      background: linear-gradient(135deg, #4f46e5, #4338ca);
      color: #ffffff;
    }
    .bubble-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 0.75rem;
    }
    .sender-name {
      font-weight: 700;
    }
    .timestamp {
      opacity: 0.7;
    }
    .bubble-text {
      white-space: pre-wrap;
    }
    .intro-message {
      max-width: 100%;
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
    }
    .try-prompt-hint {
      font-weight: 600;
      margin: 12px 0 8px;
      font-size: 0.85rem;
      color: #475569;
    }
    .quick-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .chip {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 9999px;
      padding: 6px 14px;
      font-size: 0.8rem;
      font-weight: 500;
      color: #334155;
      cursor: pointer;
      transition: all 0.15s;
    }
    .chip:hover {
      background: #eef2ff;
      border-color: #6366f1;
      color: #4f46e5;
    }

    .sources-wrap {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid #f1f5f9;
    }
    .sources-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.76rem;
      font-weight: 700;
      color: #059669;
      margin-bottom: 8px;
    }
    .source-icon {
      font-size: 16px;
    }
    .source-cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 8px;
    }
    .source-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 0.75rem;
    }
    .src-top {
      display: flex;
      justify-content: space-between;
      color: #0f172a;
    }
    .src-cost {
      font-weight: 700;
    }
    .src-bottom {
      display: flex;
      flex-direction: column;
      color: #64748b;
      margin-top: 2px;
    }

    .typing-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 12px 18px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      width: fit-content;
    }
    .typing-indicator .dot {
      width: 7px;
      height: 7px;
      background: #6366f1;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;
    }
    .typing-indicator .dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator .dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-text {
      font-size: 0.78rem;
      color: #64748b;
      margin-left: 6px;
    }
    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1.0); }
    }

    .input-container {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 8px 14px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .chat-form {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .chat-input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 0.95rem;
      padding: 8px 0;
      background: transparent;
    }
    .send-btn {
      padding: 8px 16px;
      border-radius: 8px;
    }
  `]
})
export class AiAssistantComponent implements OnInit, AfterViewChecked {
  @ViewChild('scrollContainer') scrollContainerRef!: ElementRef;

  messages: ChatMessage[] = [];
  userInput: string = '';
  loading: boolean = false;

  constructor(
    private aiService: AIService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Check if prompt was passed via query params
    this.route.queryParams.subscribe(params => {
      if (params['prompt']) {
        this.sendQuery(params['prompt']);
      }
    });
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      if (this.scrollContainerRef) {
        this.scrollContainerRef.nativeElement.scrollTop =
          this.scrollContainerRef.nativeElement.scrollHeight;
      }
    } catch {}
  }

  onSubmit(): void {
    if (!this.userInput.trim() || this.loading) return;
    const query = this.userInput.trim();
    this.userInput = '';
    this.sendQuery(query);
  }

  sendQuery(query: string): void {
    const userMsg: ChatMessage = {
      sender: 'user',
      text: query,
      timestamp: new Date()
    };
    this.messages.push(userMsg);
    this.loading = true;

    this.aiService.chat(query).subscribe({
      next: (resp) => {
        this.loading = false;
        const assistantMsg: ChatMessage = {
          sender: 'assistant',
          text: resp.answer,
          sources: resp.sources,
          latency_ms: resp.latency_ms,
          timestamp: new Date(),
          model: resp.model
        };
        this.messages.push(assistantMsg);
      },
      error: (err) => {
        this.loading = false;
        const errorMsg: ChatMessage = {
          sender: 'assistant',
          text: 'An error occurred while communicating with the AI service. Please verify server connectivity.',
          timestamp: new Date()
        };
        this.messages.push(errorMsg);
      }
    });
  }

  clearHistory(): void {
    this.messages = [];
  }

  formatMessage(text: string): string {
    // Basic markdown conversion for bold and lists
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
    return formatted;
  }
}
