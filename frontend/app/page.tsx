'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, User, Bot, Sparkles, Trophy, ChevronRight, Loader2 } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

type ViewState = 'start' | 'chat' | 'result';
type Message = { id: string; sender: 'bot' | 'user'; text: string };

export default function InterviewApp() {
  const [view, setView] = useState<ViewState>('start');
  const [candidateName, setCandidateName] = useState('');
  const [sessionId, setSessionId] = useState<number | null>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const [finalResult, setFinalResult] = useState<{ total_score: number; recommendation?: string } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateName.trim()) return;
    
    setIsTyping(true);
    try {
      const res = await fetch(`${API_BASE}/interview/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_name: candidateName }),
      });
      const data = await res.json();
      
      setSessionId(data.session_id);
      setMessages([{ id: Date.now().toString(), sender: 'bot', text: data.bot_message }]);
      setView('chat');
    } catch (error) {
      console.error('Error starting interview:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !sessionId) return;

    const userMessageText = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'user', text: userMessageText }]);
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE}/interview/${sessionId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessageText }),
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: data.bot_message }]);
      
      if (data.is_finished) {
        setTimeout(() => fetchResult(sessionId), 1500); // Small delay to read the last message
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const fetchResult = async (id: number) => {
    setIsTyping(true);
    try {
      const res = await fetch(`${API_BASE}/interview/${id}/result`);
      const data = await res.json();
      setFinalResult(data);
      setView('result');
    } catch (error) {
      console.error('Error fetching result:', error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center p-4 selection:bg-indigo-500/30">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-neutral-950 to-neutral-950 -z-10" />
      
      <AnimatePresence mode="wait">
        {view === 'start' && (
          <motion.div
            key="start"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-md"
          >
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/10 p-8 rounded-3xl shadow-2xl">
              <div className="w-16 h-16 bg-indigo-500/20 text-indigo-400 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                <Sparkles size={32} />
              </div>
              <h1 className="text-3xl font-bold text-center mb-2 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                AI Interviewer
              </h1>
              <p className="text-neutral-400 text-center mb-8 text-sm">
                Ready to test your skills? Enter your name to begin the session.
              </p>
              
              <form onSubmit={handleStart} className="space-y-4">
                <div>
                  <input
                    type="text"
                    required
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    placeholder="E.g., John Doe"
                    className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!candidateName.trim() || isTyping}
                  className="w-full bg-white text-black font-semibold rounded-xl px-4 py-3 hover:bg-neutral-200 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isTyping ? <Loader2 className="animate-spin" /> : 'Start Interview'}
                  {!isTyping && <ChevronRight size={18} />}
                </button>
              </form>
            </div>
          </motion.div>
        )}

        {view === 'chat' && (
          <motion.div
            key="chat"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="w-full max-w-3xl h-[85vh] flex flex-col bg-neutral-900/50 backdrop-blur-xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="border-b border-white/10 p-4 flex items-center gap-4 bg-black/20">
              <div className="w-10 h-10 bg-indigo-500/20 text-indigo-400 rounded-full flex items-center justify-center">
                <Bot size={20} />
              </div>
              <div>
                <h2 className="font-semibold text-neutral-200">Interview Session</h2>
                <p className="text-xs text-neutral-500">Candidate: {candidateName}</p>
              </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {messages.map((msg) => (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={msg.id}
                  className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    msg.sender === 'bot' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-neutral-800 text-neutral-300'
                  }`}>
                    {msg.sender === 'bot' ? <Bot size={16} /> : <User size={16} />}
                  </div>
                  <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    msg.sender === 'bot' 
                      ? 'bg-neutral-800/80 text-neutral-200 border border-white/5 rounded-tl-sm' 
                      : 'bg-indigo-600 text-white rounded-tr-sm'
                  }`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                  <div className="w-8 h-8 bg-indigo-500/20 text-indigo-400 rounded-full flex items-center justify-center shrink-0">
                    <Bot size={16} />
                  </div>
                  <div className="bg-neutral-800/80 border border-white/5 rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-1">
                    <div className="w-1.5 h-1.5 bg-neutral-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-neutral-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-neutral-500 rounded-full animate-bounce" />
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-black/20 border-t border-white/10">
              <form onSubmit={handleSendMessage} className="relative flex items-center">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type your answer..."
                  className="w-full bg-neutral-800/50 border border-white/10 rounded-2xl pl-5 pr-14 py-4 text-white placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || isTyping}
                  className="absolute right-2 p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-500 transition-all disabled:opacity-50 disabled:hover:bg-indigo-600 flex items-center justify-center"
                >
                  <Send size={18} className="translate-x-[1px]" />
                </button>
              </form>
            </div>
          </motion.div>
        )}

        {view === 'result' && finalResult && (
          <motion.div
            key="result"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-md text-center"
          >
             <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/10 p-10 rounded-3xl shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50" />
                
                <div className="w-20 h-20 bg-gradient-to-tr from-indigo-500 to-purple-500 text-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(99,102,241,0.4)]">
                  <Trophy size={36} />
                </div>
                
                <h2 className="text-2xl font-bold mb-2">Interview Complete</h2>
                <p className="text-neutral-400 mb-8">Great job, {candidateName}!</p>
                
                <div className="bg-black/40 rounded-2xl p-6 border border-white/5 mb-8">
                  <p className="text-sm text-neutral-400 mb-1">Final Score</p>
                  <p className="text-5xl font-black bg-gradient-to-b from-white to-neutral-500 bg-clip-text text-transparent">
                    {finalResult.total_score}
                  </p>
                  <p className="text-xs text-neutral-500 mt-2">Out of 100</p>
                </div>

                <button
                  onClick={() => {
                    setView('start');
                    setCandidateName('');
                    setSessionId(null);
                    setMessages([]);
                    setFinalResult(null);
                  }}
                  className="w-full bg-white/10 hover:bg-white/20 text-white font-medium rounded-xl px-4 py-3 transition-all"
                >
                  Start New Interview
                </button>
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
