'use client';
import React, { useState, useEffect } from 'react';
import { MessageSquareText, Send, Sparkles, User, Bot, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface ChatbotProps {
  uploadId: number;
}

export default function ChatbotDrawer({ uploadId }: ChatbotProps) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'bot'; text: string }>>([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Financial Copilot grounded strictly on your uploaded accounting workbook. How can I assist with your financial statements or ratios today?'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const quickPrompts = [
    'Explain this Balance Sheet.',
    'Why is ROE low?',
    'Explain Cash Flow.',
    'Explain Working Capital.',
    'Give business recommendations.',
    'Summarize company performance.'
  ];

  const handleSend = async (textToSend?: string) => {
    const promptText = textToSend || query;
    if (!promptText.trim()) return;

    setMessages((prev) => [...prev, { sender: 'user', text: promptText }]);
    if (!textToSend) setQuery('');
    setIsLoading(true);

    try {
      const res = await api.post('/api/chat/', {
        upload_id: uploadId,
        query: promptText
      });

      setMessages((prev) => [...prev, { sender: 'bot', text: res.data.response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'Sorry, I encountered an issue accessing the financial dataset. Please try again.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-200 flex flex-col h-[520px]">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900">AI Financial Copilot</h4>
            <p className="text-[11px] text-emerald-600 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Grounded on Active Workbook
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto my-3 space-y-3 pr-1">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'bot' && (
              <div className="w-6 h-6 rounded-lg bg-brand-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
            )}
            <div
              className={`p-3 rounded-2xl text-xs max-w-[85%] leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-brand-600 text-white font-medium rounded-br-none'
                  : 'bg-slate-100 text-slate-800 font-medium rounded-bl-none whitespace-pre-wrap'
              }`}
            >
              {m.text}
            </div>
            {m.sender === 'user' && (
              <div className="w-6 h-6 rounded-lg bg-slate-800 text-white flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-brand-600" />
            <span>Analyzing dataset...</span>
          </div>
        )}
      </div>

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-1.5 my-2">
        {quickPrompts.slice(0, 3).map((qp, i) => (
          <button
            key={i}
            onClick={() => handleSend(qp)}
            className="text-[10px] font-semibold bg-slate-100 hover:bg-brand-50 hover:text-brand-700 text-slate-600 px-2.5 py-1 rounded-full border border-slate-200 transition-colors"
          >
            {qp}
          </button>
        ))}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 pt-2 border-t border-slate-100"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about this company's financials..."
          className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="p-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl disabled:opacity-50 transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
