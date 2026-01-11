"use client";

import { useState, useEffect, useRef } from "react";
import { useUser } from "@/context/UserContext";
import ScoreGauge from "./ScoreGauge";
import ResultsPanel from "./ResultsPanel";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface ChatState {
  step: number;
  tempData: Record<string, number>;
}

interface Prediction {
  daily_score: number;
  day_classification: string;
  persona: string;
  recommendations: string[];
}

interface ApiResponse {
  bot_message: string;
  next_step: number;
  updated_data: Record<string, number>;
  prediction?: Prediction;
  acknowledgment?: string;
}

interface StepConfig {
  label: string;
  question: string;
  min: number;
  max: number;
  unit: string;
  lowLabel: string;
  highLabel: string;
  quickOptions: number[];
}

// Step configuration - frontend-driven questions for better UX
const STEP_CONFIG: Record<number, StepConfig> = {
  1: {
    label: "Sleep",
    question: "How many hours did you sleep?",
    min: 0,
    max: 24,
    unit: "hrs",
    lowLabel: "😫 None",
    highLabel: "😴 10+ hrs",
    quickOptions: [4, 5, 6, 7, 8, 9],
  },
  2: {
    label: "Work",
    question: "How intense was your work today?",
    min: 1,
    max: 10,
    unit: "",
    lowLabel: "🌴 Chill",
    highLabel: "🔥 Intense",
    quickOptions: [2, 4, 6, 8, 10],
  },
  3: {
    label: "Stress",
    question: "How stressed are you feeling?",
    min: 1,
    max: 10,
    unit: "",
    lowLabel: "😌 Calm",
    highLabel: "😰 Maxed",
    quickOptions: [2, 4, 6, 8, 10],
  },
  4: {
    label: "Mood",
    question: "How's your mood right now?",
    min: 1,
    max: 10,
    unit: "",
    lowLabel: "😔 Low",
    highLabel: "😊 Great",
    quickOptions: [2, 4, 6, 8, 10],
  },
  5: {
    label: "Screen",
    question: "Hours on screens today?",
    min: 0,
    max: 24,
    unit: "hrs",
    lowLabel: "📵 None",
    highLabel: "💻 All day",
    quickOptions: [1, 3, 5, 8, 12],
  },
  6: {
    label: "Water",
    question: "Glasses of water today?",
    min: 0,
    max: 20,
    unit: "",
    lowLabel: "🏜️ None",
    highLabel: "💧 8+",
    quickOptions: [2, 4, 6, 8, 10],
  },
};

// ============================================================================
// TOAST COMPONENT
// ============================================================================

function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 2000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 animate-slide-down">
      <div className="bg-green-500/20 border border-green-500/50 text-green-400 px-6 py-3 rounded-full backdrop-blur-sm flex items-center gap-2">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        {message}
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ChatConsole() {
  const { user, refreshSessions, refreshStats } = useUser();
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatState, setChatState] = useState<ChatState>({ step: 0, tempData: {} });
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input on step change
  useEffect(() => {
    if (inputRef.current && !showResults) {
      inputRef.current.focus();
    }
  }, [chatState.step, showResults]);

  // --- API CALL ---
  const sendMessage = async (message: string) => {
    // Allow empty message only for step 0 (start)
    if (!message.trim() && chatState.step !== 0) return;

    setIsLoading(true);
    setShowResults(false);
    setPrediction(null);

    try {
      const res = await fetch(`${API_BASE}/talk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: message,
          current_step: chatState.step,
          temp_data: chatState.tempData,
          user_id: user?.id,
        }),
      });

      const data: ApiResponse = await res.json();

      // Show acknowledgment toast if present
      if (data.acknowledgment) {
        setToast(data.acknowledgment);
      }

      setChatState((prev) => ({
        ...prev,
        step: data.next_step,
        tempData: data.updated_data,
      }));

      setInput("");
      setIsLoading(false);

      // Check if we got a prediction (final step)
      if (data.prediction) {
        setPrediction(data.prediction);
        setTimeout(() => {
          setShowResults(true);
          // Refresh user data after completing a session
          if (user) {
            refreshSessions();
            refreshStats();
          }
        }, 300);
      }
    } catch {
      setToast("⚠️ Connection error");
      setIsLoading(false);
    }
  };

  // --- QUICK SELECT ---
  const handleQuickSelect = (value: number) => {
    sendMessage(value.toString());
  };

  // --- NEW SESSION ---
  const startNewSession = () => {
    setShowResults(false);
    setPrediction(null);
    setChatState({ step: 0, tempData: {} });
    sendMessage("");
  };

  // --- INITIAL START ---
  useEffect(() => {
    sendMessage("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getProgress = () => Math.min((chatState.step / 6) * 100, 100);
  const currentConfig = STEP_CONFIG[chatState.step];

  return (
    <div className="w-full max-w-2xl flex flex-col gap-5 z-10 p-6">
      {/* Toast Notification */}
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}

      {/* ========== STATUS BAR ========== */}
      <div className="flex justify-between items-center text-xs font-mono text-slate-500 uppercase tracking-widest">
        <div className="flex items-center gap-2">
          <span className="status-dot"></span>
          <span>HabitOS_Core // Online</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Step {chatState.step}/6</span>
          <span>v2.0</span>
        </div>
      </div>

      {/* ========== PROGRESS BAR ========== */}
      <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
          style={{ width: `${getProgress()}%` }}
        />
      </div>

      {/* ========== RESULTS OR CHAT ========== */}
      {showResults && prediction ? (
        <div className="animate-slide-up">
          <div className="flex justify-center mb-6">
            <ScoreGauge score={prediction.daily_score} />
          </div>
          <ResultsPanel prediction={prediction} />
          <button
            onClick={startNewSession}
            className="w-full mt-6 py-4 glass-panel glass-panel-hover rounded-xl text-center font-semibold text-blue-400 hover:text-blue-300 transition-all duration-300 hover:scale-[1.02]"
          >
            🔄 Start New Analysis
          </button>
        </div>
      ) : (
        <>
          {/* ========== QUESTION DISPLAY ========== */}
          <div className="min-h-[80px] flex items-center justify-center text-center px-4 py-6">
            <h1 className="text-2xl md:text-3xl font-bold gradient-text">
              {chatState.step === 0
                ? "Ready for your daily check-in?"
                : currentConfig?.question || "Processing..."}
            </h1>
          </div>

          {/* ========== QUICK SELECT BUTTONS ========== */}
          {currentConfig && !isLoading && (
            <div className="space-y-4">
              {/* Scale Labels */}
              <div className="flex justify-between text-sm text-slate-400 px-4">
                <span>{currentConfig.lowLabel}</span>
                <span>{currentConfig.highLabel}</span>
              </div>

              {/* Quick Select Grid */}
              <div className="grid grid-cols-5 gap-2 px-2">
                {currentConfig.quickOptions.map((value) => (
                  <button
                    key={value}
                    onClick={() => handleQuickSelect(value)}
                    className="py-4 glass-panel rounded-xl text-white text-lg font-semibold 
                               hover:bg-blue-500/30 hover:border-blue-500/50 
                               active:scale-95 transition-all duration-150 
                               border border-white/10"
                  >
                    {value}
                    {currentConfig.unit && (
                      <span className="text-xs text-slate-500 ml-0.5">
                        {currentConfig.unit}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ========== START BUTTON (Step 0) ========== */}
          {chatState.step === 0 && !isLoading && (
            <button
              onClick={() => sendMessage("")}
              className="w-full py-5 glass-panel rounded-xl text-xl font-semibold 
                         text-blue-400 hover:text-white hover:bg-blue-500/30 
                         transition-all duration-300 border border-blue-500/30"
            >
              ▶ Start Check-in
            </button>
          )}

          {/* ========== CUSTOM INPUT ========== */}
          {currentConfig && !isLoading && (
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-lg" />

              <div className="relative glass-panel rounded-xl overflow-hidden flex">
                <input
                  ref={inputRef}
                  type="number"
                  inputMode="decimal"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
                  placeholder={`Or type ${currentConfig.min}-${currentConfig.max}...`}
                  min={currentConfig.min}
                  max={currentConfig.max}
                  className="flex-1 bg-transparent text-white text-center text-lg p-4 focus:outline-none placeholder:text-slate-600"
                />

                <button
                  onClick={() => sendMessage(input)}
                  disabled={!input.trim()}
                  className="px-5 bg-blue-500/20 hover:bg-blue-500/40 text-blue-400 transition-all disabled:opacity-30"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* ========== LOADING STATE ========== */}
          {isLoading && (
            <div className="flex justify-center py-8">
              <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            </div>
          )}
        </>
      )}
    </div>
  );
}
