import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Trash2, 
  Clock, 
  ShieldCheck, 
  Cpu, 
  ArrowRight,
  Database
} from 'lucide-react';
import { EvidenceCard } from '../components/EvidenceCard';
import { ChatResponse } from '../types';
import { api } from '../services/api';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  responseMeta?: ChatResponse;
}

interface AssistantPageProps {
  initialQuery?: string;
  onClearInitialQuery?: () => void;
}

export const AssistantPage: React.FC<AssistantPageProps> = ({
  initialQuery,
  onClearInitialQuery
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: (
        "### Welcome to VehicleGPT On-Device Intelligence\n\n" +
        "I am your local, on-edge vehicle assistant operating in **100% offline isolation**. " +
        "I interpret natural-language vehicle questions, compute answers using whitelisted deterministic analytics against local SQLite telemetry, and explain the results with zero hallucination.\n\n" +
        "You can ask me about driving range changes, fuel/energy efficiency drops, ADAS disengagements, battery thermal trends, and pre-event investigations."
      ),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (initialQuery) {
      handleSendMessage(initialQuery);
      if (onClearInitialQuery) onClearInitialQuery();
    }
  }, [initialQuery]);

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputText.trim();
    if (!textToSend || loading) return;

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputText('');
    setLoading(true);

    try {
      const resp = await api.queryChat(textToSend);
      const assistantMsg: Message = {
        id: `asst-${Date.now()}`,
        sender: 'assistant',
        text: resp.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        responseMeta: resp
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: "Error: Failed to process query locally. Ensure the backend edge service is running.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([messages[0]]);
  };

  const sampleChips = [
    "Why has my driving range reduced over the last two weeks?",
    "When did fuel efficiency show the largest drop?",
    "Show all ADAS disengagement events from yesterday.",
    "What happened before the battery overheating warning?",
    "Compare energy consumption between city and highway driving.",
    "What were the warning codes before the last vehicle fault?",
    "Show telemetry from the year 2021."
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-5xl mx-auto space-y-4">
      {/* Top Assistant Status Header */}
      <div className="glass-panel px-4 py-3 rounded-xl border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-white">VehicleGPT Natural Language Agent</span>
              <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800/40">
                Offline Active
              </span>
            </div>
            <p className="text-xs text-slate-400">Strict Read-Only Access • Deterministic Analytics First</p>
          </div>
        </div>

        <button
          onClick={clearChat}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 transition-colors"
          title="Clear Conversation"
        >
          <Trash2 className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Clear</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 glass-panel p-4 sm:p-6 rounded-2xl border border-slate-800 overflow-y-auto space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${
              msg.sender === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className={`h-8 w-8 rounded-xl flex items-center justify-center shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'bg-slate-800 text-blue-400 border border-slate-700'
              }`}
            >
              {msg.sender === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>

            <div className={`max-w-[85%] sm:max-w-[75%] space-y-1`}>
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-none'
                    : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none shadow-lg'
                }`}
              >
                {/* Markdown text rendered cleanly */}
                <div className="prose prose-invert prose-sm max-w-none space-y-2 whitespace-pre-wrap">
                  {msg.text}
                </div>

                {/* Evidence Drawer if available */}
                {msg.responseMeta?.evidence && (
                  <EvidenceCard
                    evidence={msg.responseMeta.evidence}
                    source={msg.responseMeta.source}
                    latencyMs={msg.responseMeta.latency_ms}
                    confidence={msg.responseMeta.confidence}
                    modelName={msg.responseMeta.model_name}
                  />
                )}
              </div>

              <span className="text-[10px] text-slate-500 font-mono px-1 block">
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="h-8 w-8 rounded-xl bg-slate-800 text-blue-400 border border-slate-700 flex items-center justify-center">
              <Bot className="h-4 w-4 animate-spin" />
            </div>
            <div className="p-4 rounded-2xl rounded-tl-none bg-slate-900 border border-slate-800 text-slate-400 text-sm flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-400 animate-pulse" />
              <span>Analyzing historical records and generating evidence-grounded answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Question Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
        <span className="text-slate-500 text-xs shrink-0 font-medium">Suggested:</span>
        {sampleChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(chip)}
            disabled={loading}
            className="px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-blue-600/20 text-slate-300 hover:text-blue-300 border border-slate-800 whitespace-nowrap transition-colors shrink-0 disabled:opacity-50"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input Box Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="glass-panel p-2 rounded-2xl border border-slate-800 flex items-center gap-2 bg-slate-950/80"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask a question about your vehicle (e.g. 'Why did my range drop?')..."
          disabled={loading}
          className="flex-1 bg-transparent px-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || loading}
          className="h-10 w-10 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white flex items-center justify-center transition-colors shadow-md shadow-blue-600/30 shrink-0"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
};
