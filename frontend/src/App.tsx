import React, { useState, useRef, useEffect } from "react";
import {
  Terminal,
  Box,
  Settings,
  Cpu,
  ShieldAlert,
  GitBranch,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import TelemetryHUD from "./components/TelemetryHUD";
import ZVectorMonitor from "./components/ZVectorMonitor";
import CommandConsole from "./components/CommandConsole";
import ValidationBuildEngine from "./components/ValidationForge";
import { useTelemetryPolling } from "./hooks/useTelemetryPolling";

type Message = {
  id: string;
  role: "user" | "system";
  content: string;
  timestamp: Date | string;
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "system-init",
      role: "system",
      content: "CORE ENGINE INITIALIZED. WAITING FOR DIRECTIVES.",
      timestamp: new Date(),
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isBuildEngineOpen, setIsBuildEngineOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const apiBase = (
    import.meta.env.VITE_CORE_API_URL || "http://localhost:8000"
  ).replace(/\/$/, "");
  const wsUrl = apiBase.replace(/^http/, "ws") + "/ws";
  const { data: telemetry, connected: telemetryConnected } =
    useTelemetryPolling({ apiBase });

  // Initialisiere Websocket (fuer Event-Streaming)
  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimer: any;

    const connect = () => {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WS] Connected to Core");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "chat_chunk" && data.content) {
            setMessages((prev) => {
              const last = prev[prev.length - 1];
              if (last && last.role === "system" && last.id === data.msg_id) {
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: last.content + data.content },
                ];
              } else {
                return [
                  ...prev,
                  {
                    id: data.msg_id || Date.now().toString(),
                    role: "system",
                    content: data.content,
                    timestamp: new Date(),
                  },
                ];
              }
            });
          }
        } catch (e) {
          console.error("[WS] Parse error", e);
        }
      };

      ws.onclose = () => {
        console.log("[WS] Disconnected. Reconnecting in 5s...");
        reconnectTimer = setTimeout(connect, 5000);
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (wsRef.current) wsRef.current.close();
    };
  }, [wsUrl]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleCommand = async (cmd: string) => {
    if (!cmd.trim()) return;

    const newMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: cmd,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMsg]);
    setIsProcessing(true);

    // Wenn der Befehl "audit" oder "build_engine" enthaelt, oeffne die Build-Engine testweise
    if (
      cmd.toLowerCase().includes("build_engine") ||
      cmd.toLowerCase().includes("audit")
    ) {
      setIsBuildEngineOpen(true);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

    try {
      const res = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: cmd, mode: "fast" }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!res.ok) throw new Error(`System error: ${res.status}`);

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + "-sys",
          role: "system",
          content: data.response || "No response generated.",
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + "-err",
          role: "system",
          content: "[ERROR] Core API nicht erreichbar oder Timeout.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBuildEngineRotate = () => {
    // Dummy-Action fuer die UI Demonstration
    console.log("Rotating Build-Engine...");
  };

  return (
    <div className="flex flex-col h-screen bg-[#121212] text-[#E0E0E0] font-sans overflow-hidden">
      {/* Top Bar: Telemetry HUD */}
      <header className="flex-none bg-[#0A0A0A] border-b border-[#333] px-6 py-2.5 flex items-center justify-between z-20 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
        <div className="flex items-center gap-3">
          <Box size={20} className="text-[#FFB300]" />
          <h1 className="text-sm font-mono tracking-[0.2em] uppercase font-bold text-[#E0E0E0]">
            CORE COCKPIT
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <TelemetryHUD data={telemetry} connected={telemetryConnected} />
          <ZVectorMonitor data={telemetry} connected={telemetryConnected} />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsBuildEngineOpen(!isBuildEngineOpen)}
            className={`p-1.5 rounded-lg border transition-all flex items-center gap-2
              ${isBuildEngineOpen ? "bg-[#FFB300] text-[#121212] border-[#FFB300]" : "bg-[#1A1A1A] text-[#A0A0A0] border-[#333] hover:text-[#E0E0E0] hover:border-[#666]"}`}
            title="Validation Build-Engine"
          >
            <GitBranch size={16} />
            <span className="text-[10px] uppercase font-mono tracking-wider px-1">
              Build-Engine
            </span>
          </button>
          <div className="w-px h-6 bg-[#333] mx-1"></div>
          <button
            className="text-[#666] hover:text-[#E0E0E0] transition-colors p-1"
            title="Settings"
          >
            <Settings size={18} />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex relative overflow-hidden">
        {/* Output Area (Chat / Logs) */}
        <div className="flex-1 overflow-y-auto px-6 py-8 pb-32">
          <div className="max-w-5xl mx-auto space-y-6">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg p-4 font-mono text-sm leading-relaxed whitespace-pre-wrap
                    ${
                      msg.role === "user"
                        ? "bg-[#1A1A1A] border border-[#333] text-[#E0E0E0]"
                        : "bg-transparent border-l-2 border-[#FFB300] pl-6 text-[#A0A0A0]"
                    }`}
                >
                  {msg.role === "user" && (
                    <div className="text-[10px] text-[#666] uppercase tracking-wider mb-2 flex items-center gap-2">
                      <Terminal size={10} /> DIRECTIVE
                    </div>
                  )}
                  {msg.content}
                </div>
              </motion.div>
            ))}
            {isProcessing && (
              <div className="flex justify-start">
                <div className="bg-transparent border-l-2 border-[#333] pl-6 text-[#666] font-mono text-sm uppercase flex items-center gap-3">
                  <div className="w-2 h-2 bg-[#FFB300] rounded-full animate-pulse"></div>
                  Processing...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Sliding Validation Build-Engine Panel */}
        <ValidationBuildEngine
          isOpen={isBuildEngineOpen}
          onClose={() => setIsBuildEngineOpen(false)}
          isRotating={false}
          onRotate={handleBuildEngineRotate}
          logs={[
            {
              id: "1",
              source: "Architect",
              severity: "info",
              message:
                "Keine strukturellen Verletzungen in der API-Route gefunden.",
            },
            {
              id: "2",
              source: "Security",
              severity: "warning",
              message:
                'CORS-Headers koennten in der Produktion zu offen sein. (allow_origins=["*"])',
            },
            {
              id: "3",
              source: "Performance",
              severity: "error",
              message:
                "Thread-Locking in ChromaDB koennte bei >10 req/s zu Timeouts fuehren.",
            },
          ]}
        />
      </main>

      {/* Bottom Command Interface */}
      <div className="absolute bottom-0 left-0 right-0">
        <CommandConsole onExecute={handleCommand} isProcessing={isProcessing} />
      </div>
    </div>
  );
}
