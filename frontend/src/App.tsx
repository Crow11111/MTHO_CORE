import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, Code2, Settings, Sparkles, Cpu, Menu, Headphones, Mic, Volume2, RefreshCw, Link } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

type Message = {
  id: string;
  role: 'user' | 'agent' | 'external';
  sender?: string;
  content: string;
  timestamp: Date | string;
};

type ServiceStatus = 'online' | 'offline' | 'restarting';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'agent',
      sender: 'Atlas',
      content: 'Hello. I am the ATLAS Dev Agent. How can we build today?',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showAudioProfiles, setShowAudioProfiles] = useState(false);
  const [activeProfile, setActiveProfile] = useState('Zen Voice');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const apiBase = (import.meta.env.VITE_ATLAS_API_URL || 'http://localhost:8000').replace(/\/$/, '');
  const wsUrl = apiBase.replace(/^http/, 'ws') + '/ws';

  // Status Indicators State
  const [services, setServices] = useState<Record<string, ServiceStatus>>({
    'System': 'online',
    'Comm Chain': 'offline',
    'Database': 'online',
    'Worker': 'online'
  });
  const [wsConnected, setWsConnected] = useState(false);

  // Beim Start: Chat-Historie vom Backend laden (falls vorhanden)
  useEffect(() => {
    fetch(`${apiBase}/api/chat/history`)
      .then((res) => res.ok ? res.json() : [])
      .then((list: Message[]) => {
        if (Array.isArray(list) && list.length > 0) {
          const normalized = list.map((m) => ({
            ...m,
            timestamp: typeof m.timestamp === 'string' ? new Date(m.timestamp) : m.timestamp,
          }));
          setMessages(normalized);
        }
      })
      .catch(() => {});
  }, [apiBase]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // WebSocket: connect, reconnect when disconnected, handle chat:reply, system:event, status:update
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    const reconnectDelayMs = 5000;

    const connect = () => {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onopen = () => setWsConnected(true);
      ws.onclose = () => {
        setWsConnected(false);
        wsRef.current = null;
        reconnectTimer = setTimeout(connect, reconnectDelayMs);
      };
      ws.onerror = () => setWsConnected(false);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const { type, payload } = data;
          if (type === 'chat:reply' && payload) {
            const msg: Message = {
              id: payload.id || Date.now().toString(),
              role: payload.role || 'agent',
              sender: payload.sender || 'Atlas',
              content: payload.content ?? '',
              timestamp: payload.timestamp ? new Date(payload.timestamp) : new Date(),
            };
            setMessages((prev) => [...prev, msg]);
            setIsTyping(false);
          } else if (type === 'system:event' && payload) {
            const msg: Message = {
              id: payload.id || Date.now().toString(),
              role: payload.role || 'external',
              sender: payload.sender || 'System',
              content: payload.content ?? '',
              timestamp: payload.timestamp ? new Date(payload.timestamp) : new Date(),
            };
            setMessages((prev) => [...prev, msg]);
          } else if (type === 'status:update' && payload) {
            const { service, status } = payload;
            if (service && status) setServices((prev) => ({ ...prev, [service]: status }));
          }
        } catch (_) {}
      };
    };

    connect();
    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
      wsRef.current = null;
    };
  }, [wsUrl]);

  const simulateExternalMessage = (sender: string = 'Service-B (Auth)', content: string = 'User token validation failed for session #891. Requesting re-authentication.') => {
    const extMsg: Message = {
      id: Date.now().toString(),
      role: 'external',
      sender,
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, extMsg]);
  };

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      sender: 'You',
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newUserMsg]);
    setInput('');
    setIsTyping(true);

    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'chat:send', content: newUserMsg.content }));
    } else {
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        sender: 'Atlas',
        content: 'Nicht verbunden. Bitte ATLAS-CORE-API starten (z. B. uvicorn) und Seite neu laden.',
        timestamp: new Date(),
      }]);
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleRestartService = async (name: string) => {
    setServices(prev => ({ ...prev, [name]: 'restarting' }));
    try {
      const res = await fetch(`${apiBase}/api/services/${encodeURIComponent(name)}/restart`, { method: 'POST' });
      const data = await res.json().catch(() => ({}));
      if (data.success) {
        setTimeout(() => setServices(prev => ({ ...prev, [name]: 'online' })), 2500);
      } else {
        setServices(prev => ({ ...prev, [name]: 'offline' }));
      }
    } catch {
      setServices(prev => ({ ...prev, [name]: 'offline' }));
    }
  };

  const audioProfiles = ['Zen Voice', 'Director', 'Analyst', 'Mute'];

  const getStatusColor = (status: ServiceStatus) => {
    switch(status) {
      case 'online': return 'bg-[#4CAF50] shadow-[0_0_8px_rgba(76,175,80,0.4)]';
      case 'offline': return 'bg-[#F44336] shadow-[0_0_8px_rgba(244,67,54,0.4)]';
      case 'restarting': return 'bg-[#FFC107] shadow-[0_0_8px_rgba(255,193,7,0.4)]';
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#1C1C1C] text-[#E0E0E0] font-sans selection:bg-[#444]">
      {/* Sidebar - Dark Minimalist */}
      <aside className="hidden md:flex flex-col w-20 items-center py-8 border-r border-[#2A2A2A] bg-[#222222]">
        <div className="p-3 bg-[#333] rounded-2xl mb-8 shadow-inner">
          <Cpu className="w-6 h-6 text-[#A0A0A0]" />
        </div>
        <nav className="flex flex-col gap-6 flex-1 relative">
          <button className="p-3 text-[#777] hover:text-[#E0E0E0] hover:bg-[#333] rounded-xl transition-colors" title="Terminal">
            <Terminal className="w-5 h-5" />
          </button>
          <button className="p-3 text-[#777] hover:text-[#E0E0E0] hover:bg-[#333] rounded-xl transition-colors" title="Code">
            <Code2 className="w-5 h-5" />
          </button>
          
          {/* Audio Profile Button */}
          <div className="relative">
            <button 
              onClick={() => setShowAudioProfiles(!showAudioProfiles)}
              className={`p-3 rounded-xl transition-colors ${showAudioProfiles ? 'bg-[#333] text-[#E0E0E0]' : 'text-[#777] hover:text-[#E0E0E0] hover:bg-[#333]'}`}
              title="Audio Profiles"
            >
              <Headphones className="w-5 h-5" />
            </button>
            
            {/* Audio Profiles Mock Menu */}
            <AnimatePresence>
              {showAudioProfiles && (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="absolute left-16 top-0 w-48 bg-[#2A2A2A] border border-[#3A3A3A] rounded-xl shadow-xl overflow-hidden z-50"
                >
                  <div className="px-4 py-3 border-b border-[#3A3A3A] text-xs font-mono text-[#888] uppercase tracking-wider">
                    Audio Profiles
                  </div>
                  <div className="p-2 flex flex-col gap-1">
                    {audioProfiles.map(profile => (
                      <button 
                        key={profile}
                        onClick={() => { setActiveProfile(profile); setShowAudioProfiles(false); }}
                        className={`text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${activeProfile === profile ? 'bg-[#3A3A3A] text-[#E0E0E0]' : 'text-[#999] hover:bg-[#333] hover:text-[#E0E0E0]'}`}
                      >
                        {profile}
                        {activeProfile === profile && <Volume2 className="w-3.5 h-3.5 text-[#888]" />}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button className="p-3 text-[#777] hover:text-[#E0E0E0] hover:bg-[#333] rounded-xl transition-colors" title="AI Features">
            <Sparkles className="w-5 h-5" />
          </button>

          {/* Trigger External Message (Debug/Demo) */}
          <button 
            onClick={() => simulateExternalMessage()}
            className="p-3 text-[#777] hover:text-[#D0D6F5] hover:bg-[#2A2D3D] rounded-xl transition-colors mt-auto" 
            title="Simulate External Intercept"
          >
            <Link className="w-5 h-5" />
          </button>
        </nav>
        <button className="p-3 text-[#777] hover:text-[#E0E0E0] hover:bg-[#333] rounded-xl transition-colors mt-6" title="Settings">
          <Settings className="w-5 h-5" />
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full mx-auto w-full relative">
        {/* Header */}
        <header className="flex flex-col lg:flex-row lg:items-center justify-between px-6 py-4 bg-[#1C1C1C]/90 backdrop-blur-md sticky top-0 z-10 border-b border-[#2A2A2A]/50 gap-4">
          <div className="flex items-center gap-3">
            <button className="md:hidden p-2 -ml-2 text-[#777]">
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-lg font-medium tracking-tight text-[#E0E0E0]">ATLAS</h1>
              <p className="text-xs text-[#777] font-mono tracking-wider uppercase">Dev Agent</p>
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-[#252525] border border-[#333] rounded-full mr-2">
              <Mic className="w-3.5 h-3.5 text-[#888]" />
              <span className="text-[11px] text-[#A0A0A0] font-mono">{activeProfile}</span>
            </div>
            <div className="flex items-center gap-2 bg-[#222] px-2.5 py-1.5 rounded-md border border-[#2A2A2A]">
              <span className={`flex h-2 w-2 rounded-full ${wsConnected ? 'bg-[#4CAF50] shadow-[0_0_8px_rgba(76,175,80,0.4)]' : 'bg-[#F44336]'}`}></span>
              <span className="text-[11px] text-[#888] font-mono uppercase tracking-wide">Backend</span>
            </div>
            {Object.entries(services).map(([name, status]) => (
              <div key={name} className="flex items-center gap-2 bg-[#222] px-2.5 py-1.5 rounded-md border border-[#2A2A2A]">
                <span className={`flex h-2 w-2 rounded-full ${getStatusColor(status as ServiceStatus)}`}></span>
                <span className="text-[11px] text-[#888] font-mono uppercase tracking-wide">{name}</span>
                {status === 'offline' && (
                  <button 
                    onClick={() => handleRestartService(name)}
                    className="ml-1 p-1 hover:bg-[#333] rounded text-[#F44336] hover:text-[#ff7961] transition-colors"
                    title={`Restart ${name}`}
                  >
                    <RefreshCw className="w-3 h-3" />
                  </button>
                )}
                {status === 'restarting' && (
                  <RefreshCw className="w-3 h-3 ml-1 text-[#FFC107] animate-spin" />
                )}
              </div>
            ))}
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-8 scroll-smooth pb-32 max-w-5xl mx-auto w-full">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className={`flex flex-col max-w-[85%] ${msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}
              >
                <div className="flex items-center gap-2 mb-1.5 px-1">
                  <span className={`text-[10px] font-mono uppercase tracking-widest ${msg.role === 'external' ? 'text-[#8A94C9]' : 'text-[#666]'}`}>
                    {msg.sender || (msg.role === 'user' ? 'You' : 'Atlas')}
                  </span>
                </div>
                <div
                  className={`px-5 py-3.5 rounded-2xl text-[15px] leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-[#333] text-[#E0E0E0] rounded-tr-sm'
                      : msg.role === 'external'
                      ? 'bg-[#2A2D3D] border border-[#3A3F58] text-[#D0D6F5] rounded-tl-sm shadow-sm'
                      : 'bg-[#252525] border border-[#333] text-[#CCCCCC] rounded-tl-sm shadow-sm'
                  }`}
                >
                  {msg.content}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col max-w-[85%] mr-auto items-start"
            >
              <div className="flex items-center gap-2 mb-1.5 px-1">
               <span className="text-[10px] font-mono text-[#666] uppercase tracking-widest">Atlas</span>
              </div>
              <div className="px-5 py-4 rounded-2xl bg-[#252525] border border-[#333] rounded-tl-sm shadow-sm flex items-center gap-1.5">
                <motion.div
                  className="w-1.5 h-1.5 bg-[#666] rounded-full"
                  animate={{ y: [0, -3, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-1.5 h-1.5 bg-[#666] rounded-full"
                  animate={{ y: [0, -3, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="w-1.5 h-1.5 bg-[#666] rounded-full"
                  animate={{ y: [0, -3, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                />
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 md:p-6 bg-gradient-to-t from-[#1C1C1C] via-[#1C1C1C] to-transparent">
          <div className="max-w-4xl mx-auto">
            <form
              onSubmit={handleSend}
              className="relative flex items-end gap-2 bg-[#252525] border border-[#333] rounded-2xl shadow-sm p-2 focus-within:ring-1 focus-within:ring-[#555] focus-within:border-[#555] transition-all"
            >
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe what you want to build..."
                className="w-full max-h-32 min-h-[44px] bg-transparent resize-none outline-none py-2.5 px-3 text-[15px] text-[#E0E0E0] placeholder:text-[#666]"
                rows={1}
              />
              <button
                type="submit"
                disabled={!input.trim() || isTyping}
                className="p-2.5 bg-[#3A3A3A] text-[#E0E0E0] rounded-xl hover:bg-[#4A4A4A] disabled:opacity-50 disabled:hover:bg-[#3A3A3A] transition-colors flex-shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="text-center mt-3">
               <p className="text-[10px] text-[#555] font-mono tracking-wide">ATLAS DEV AGENT • V1.0.0</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
