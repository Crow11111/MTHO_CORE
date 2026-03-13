import React from 'react';
import { motion } from 'motion/react';
import { ShieldAlert, Flame, Repeat } from 'lucide-react';
import type { TelemetryData } from '../hooks/useTelemetryPolling';

type Props = {
  data: TelemetryData | null;
  connected: boolean;
};

export default function ZVectorMonitor({ data, connected }: Props) {
  if (!connected || !data || !data.shell) {
    return null;
  }

  const { shell } = data;
  
  const zVector = shell.z_vector;
  const zProgress = Math.min(100, Math.max(0, ((zVector - 0.049) / (0.9 - 0.049)) * 100));
  const isZCritical = zVector > 0.7;

  const tokenPressure = shell.total_tokens;
  const tokenMax = shell.token_kill_threshold || 233000;
  const tokenProgress = Math.min(100, Math.max(0, (tokenPressure / tokenMax) * 100));
  const isTokenCritical = tokenProgress > 80;

  const loopCount = shell.call_count;
  const loopMax = shell.max_iterations || 13;
  const loopProgress = Math.min(100, Math.max(0, (loopCount / loopMax) * 100));
  const isLoopCritical = loopProgress > 80;

  const getHeatColor = (progress: number) => {
    if (progress > 85) return 'text-[#F44336] shadow-[#F44336]'; // Rote Hitze
    if (progress > 60) return 'text-[#FF9800] shadow-[#FF9800]'; // Orange Hitze
    return 'text-[#4CAF50] shadow-[#4CAF50]'; // Gruen OK
  };

  const getHeatBgColor = (progress: number) => {
    if (progress > 85) return 'bg-[#F44336]'; 
    if (progress > 60) return 'bg-[#FF9800]'; 
    return 'bg-[#4CAF50]'; 
  };

  return (
    <div className="flex flex-wrap items-center gap-2 border-l border-[#333] pl-3 ml-1">
      
      {/* Z-Vector Resistance */}
      <div 
        className={`flex flex-col gap-1 px-2.5 py-1.5 bg-[#1C1C1C] border border-[#2A2A2A] rounded-lg min-w-[120px] relative overflow-hidden transition-all duration-300
          ${isZCritical ? 'border-[#F44336] bg-[#2A1111]' : ''}
        `}
      >
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center gap-1.5">
            <ShieldAlert className={`w-3.5 h-3.5 ${getHeatColor(zProgress)}`} />
            <span className="text-[10px] font-mono text-[#A0A0A0] uppercase tracking-wider">Z-VECTOR</span>
          </div>
          <span className={`text-[11px] font-mono font-bold ${getHeatColor(zProgress)}`}>
            {zVector.toFixed(3)}
          </span>
        </div>
        <div className="h-1 w-full bg-[#333] rounded-full overflow-hidden z-10">
          <motion.div 
            className={`h-full ${getHeatBgColor(zProgress)} shadow-[0_0_8px_currentColor]`}
            initial={{ width: 0 }}
            animate={{ width: `${zProgress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        {/* Glow effect background */}
        {isZCritical && (
          <motion.div 
            className="absolute inset-0 bg-[#F44336] opacity-10 blur-md pointer-events-none"
            animate={{ opacity: [0.05, 0.2, 0.05] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
      </div>

      {/* Token Pressure / Heat */}
      <div 
        className={`flex flex-col gap-1 px-2.5 py-1.5 bg-[#1C1C1C] border border-[#2A2A2A] rounded-lg min-w-[140px] relative overflow-hidden transition-all duration-300
          ${isTokenCritical ? 'border-[#F44336] bg-[#2A1111]' : ''}
        `}
      >
        <div className="flex items-center justify-between z-10">
          <div className="flex items-center gap-1.5">
            <Flame className={`w-3.5 h-3.5 ${getHeatColor(tokenProgress)}`} />
            <span className="text-[10px] font-mono text-[#A0A0A0] uppercase tracking-wider">PRESSURE</span>
          </div>
          <span className={`text-[11px] font-mono font-bold ${getHeatColor(tokenProgress)}`}>
            {(tokenPressure / 1000).toFixed(1)}k
          </span>
        </div>
        <div className="h-1 w-full bg-[#333] rounded-full overflow-hidden z-10 relative">
          <motion.div 
            className={`h-full ${getHeatBgColor(tokenProgress)} shadow-[0_0_8px_currentColor]`}
            initial={{ width: 0 }}
            animate={{ width: `${tokenProgress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        {/* Glow effect background */}
        {isTokenCritical && (
          <motion.div 
            className="absolute inset-0 bg-[#FF9800] opacity-10 blur-md pointer-events-none"
            animate={{ opacity: [0.05, 0.2, 0.05] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          />
        )}
      </div>

      {/* Iteration Loops */}
      <div 
        className={`flex items-center gap-2 px-2.5 py-1.5 bg-[#1C1C1C] border border-[#2A2A2A] rounded-lg relative overflow-hidden transition-all duration-300
          ${isLoopCritical ? 'border-[#F44336] bg-[#2A1111]' : ''}
        `}
      >
        <Repeat className={`w-3.5 h-3.5 ${getHeatColor(loopProgress)}`} />
        <span className="text-[11px] font-mono text-[#A0A0A0] uppercase">
          LOOP <span className={`font-bold ml-1 ${getHeatColor(loopProgress)}`}>{loopCount}/{loopMax}</span>
        </span>
      </div>

    </div>
  );
}
