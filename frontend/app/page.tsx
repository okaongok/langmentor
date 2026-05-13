'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, Plus, History, Trash2, Bot, User, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface Session {
  id: string;
  title: string;
  updated_at: string;
}

function generateSessionId() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: '你好！我是 LangMentor，你的 AI 语言学习助手。有什么我可以帮你的吗？' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>(generateSessionId);
  const [sessions, setSessions] = useState<Session[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    const storedId = localStorage.getItem('session_id');
    if (storedId) {
      setSessionId(storedId);
      fetch(`/api/sessions/${storedId}`)
        .then(res => res.ok && res.json())
        .then(data => {
          if (data?.messages?.length > 0) {
            setMessages(data.messages.map((m: any) => ({ role: m.role, content: m.content })));
          }
        })
        .catch(() => {});
    }
  }, []);

  useEffect(() => {
    if (mounted) {
      localStorage.setItem('session_id', sessionId);
    }
  }, [sessionId, mounted]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadHistory = () => {
    fetch('/api/sessions?user_id=anonymous')
      .then(res => res.ok && res.json())
      .then(data => setSessions(data || []))
      .catch(() => {});
  };

  const selectSession = (id: string) => {
    fetch(`/api/sessions/${id}`)
      .then(res => res.ok && res.json())
      .then(data => {
        if (data?.messages?.length > 0) {
          setMessages(data.messages.map((m: any) => ({ role: m.role, content: m.content })));
          setSessionId(id);
          localStorage.setItem('session_id', id);
        }
      })
      .catch(() => {});
  };

  const deleteSession = (id: string) => {
    fetch(`/api/sessions/${id}`, { method: 'DELETE' })
      .then(res => {
        if (res.ok) {
          setSessions(prev => prev.filter(s => s.id !== id));
          if (id === sessionId) {
            createNewSession();
          }
        }
      })
      .catch(() => {});
  };

  const createNewSession = () => {
    const newId = generateSessionId();
    setSessionId(newId);
    localStorage.setItem('session_id', newId);
    setMessages([
      { role: 'assistant', content: '你好！我是 LangMentor，你的 AI 语言学习助手。有什么我可以帮你的吗？' },
    ]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: '' },
    ]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });

      if (!response.ok || !response.body) throw new Error('Network error');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                assistantMessage += data.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    role: 'assistant',
                    content: assistantMessage,
                  };
                  return newMessages;
                });
                await new Promise((r) => setTimeout(r, 30));
              }
            } catch {}
          }
        }
      }
    } catch (error) {
      setMessages((prev) => {
        const newMessages = [...prev];
        if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'assistant') {
          newMessages[newMessages.length - 1] = {
            role: 'assistant',
            content: '抱歉，服务暂时不可用，请稍后再试。',
          };
        } else {
          newMessages.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后再试。' });
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 flex flex-col">
        <header className="bg-white/80 backdrop-blur-md border-b sticky top-0 z-50">
          <div className="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-200">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
                  LangMentor
                </h1>
                <p className="text-xs text-slate-400">AI 语言学习助手</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger className="gap-2 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-3">
                    <History className="w-4 h-4" />
                    历史
                  </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-72 max-h-80 overflow-y-auto">
                  <div className="px-3 py-2 text-sm font-medium text-slate-500 sticky top-0 bg-popover">历史会话</div>
                  <DropdownMenuSeparator />
                  {sessions.length === 0 ? (
                    <div className="px-3 py-8 text-sm text-slate-400 text-center">暂无历史会话</div>
                  ) : (
                    sessions.map((s) => (
                      <div key={s.id} className="flex items-center group p-1 cursor-pointer hover:bg-accent rounded-md mx-1" onClick={() => selectSession(s.id)}>
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-col">
                            <span className="truncate max-w-[180px]">{s.title}</span>
                            <span className="text-xs text-slate-400">
                              {new Date(s.updated_at).toLocaleString('zh-CN')}
                            </span>
                          </div>
                        </div>
                        <div
                          role="button"
                          tabIndex={0}
                          title="删除会话"
                          className="h-8 w-8 flex items-center justify-center rounded-md opacity-0 group-hover:opacity-100 mr-1 cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-opacity"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteSession(s.id);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.stopPropagation();
                              deleteSession(s.id);
                            }
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </div>
                      </div>
                    ))
                  )}
                </DropdownMenuContent>
              </DropdownMenu>

              <Button
                size="sm"
                onClick={createNewSession}
                className="gap-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
              >
                <Plus className="w-4 h-4" />
                新会话
              </Button>
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6 flex flex-col">
          <ScrollArea className="flex-1 rounded-2xl bg-white shadow-sm border">
            <div ref={scrollRef} className="p-6 space-y-6">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-blue-500 to-cyan-500'
                      : 'bg-gradient-to-br from-violet-500 to-indigo-600'
                  }`}>
                    {msg.role === 'user' ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-white" />
                    )}
                  </div>
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-blue-500 to-cyan-500 text-white'
                        : 'bg-slate-100 text-slate-800'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-slate-100 rounded-2xl px-4 py-3">
                    <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          <div className="mt-4 bg-white rounded-2xl shadow-sm border p-2">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="输入你的问题..."
                disabled={isLoading}
                className="flex-1 border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent"
              />
              <Button
                type="submit"
                disabled={isLoading || !input.trim()}
                size="icon"
                className="rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
              >
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </div>
        </main>
      </div>
    );
  }
