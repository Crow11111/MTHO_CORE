import React from "react";
import { RefreshCw, Code2, Cpu, Shield, Activity, Save } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

type AuditLog = {
  id: string;
  source: "Architect" | "Security" | "Performance" | "UI/UX";
  message: string;
  severity: "info" | "warning" | "error";
};

type Props = {
  isOpen: boolean;
  onClose: () => void;
  logs: AuditLog[];
  isRotating: boolean;
  onRotate: () => void;
};

export default function ValidationBuildEngine({
  isOpen,
  onClose,
  logs,
  isRotating,
  onRotate,
}: Props) {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ x: "100%", opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: "100%", opacity: 0 }}
      transition={{ type: "spring", damping: 25, stiffness: 200 }}
      className="fixed inset-y-0 right-0 w-[500px] bg-[#121212] border-l border-[#333]
                 shadow-[-20px_0_40px_rgba(0,0,0,0.5)] z-50 flex flex-col"
    >
      <div className="flex items-center justify-between p-4 border-b border-[#333]">
        <div className="flex items-center gap-2">
          <Code2 size={20} className="text-[#FFB300]" />
          <h2 className="font-mono text-sm uppercase tracking-wider text-[#E0E0E0] font-semibold">
            Validation Build-Engine
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-[#666] hover:text-[#E0E0E0] p-1 rounded transition-colors"
        >
          X
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs">
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full opacity-50 space-y-4">
            <Cpu size={48} className="text-[#666]" />
            <span className="text-center text-[#A0A0A0]">
              Warten auf Audit-Daten.
              <br />
              Kein aktiver Plan geladen.
            </span>
          </div>
        ) : (
          <AnimatePresence>
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg border flex gap-3
                  ${
                    log.severity === "error"
                      ? "border-[#FF5252] bg-[#2A1616]"
                      : log.severity === "warning"
                        ? "border-[#FFB300] bg-[#2A2312]"
                        : "border-[#333] bg-[#1A1A1A]"
                  }`}
              >
                <div className="mt-0.5">
                  {log.severity === "error" && (
                    <Shield size={14} className="text-[#FF5252]" />
                  )}
                  {log.severity === "warning" && (
                    <Activity size={14} className="text-[#FFB300]" />
                  )}
                  {log.severity === "info" && (
                    <Cpu size={14} className="text-[#A0A0A0]" />
                  )}
                </div>
                <div>
                  <span
                    className={`uppercase font-bold block mb-1 tracking-wider
                    ${
                      log.severity === "error"
                        ? "text-[#FF5252]"
                        : log.severity === "warning"
                          ? "text-[#FFB300]"
                          : "text-[#A0A0A0]"
                    }`}
                  >
                    [{log.source}]
                  </span>
                  <span className="text-[#D0D0D0] leading-relaxed">
                    {log.message}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      <div className="p-4 border-t border-[#333] bg-[#0A0A0A]">
        <button
          onClick={onRotate}
          disabled={isRotating}
          className="w-full py-3 px-4 rounded-lg bg-[#222] border border-[#333] hover:border-[#FFB300]
                     text-[#E0E0E0] font-mono text-sm uppercase tracking-widest transition-all
                     flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <RefreshCw
            size={16}
            className={
              isRotating
                ? "animate-spin text-[#FFB300]"
                : "group-hover:text-[#FFB300]"
            }
          />
          {isRotating ? "Iteriere Plan..." : "Trigger Rotation"}
        </button>
      </div>
    </motion.div>
  );
}
