"use client";

interface Prediction {
    daily_score: number;
    day_classification: string;
    persona: string;
    recommendations: string[];
}

interface ResultsPanelProps {
    prediction: Prediction;
}

export default function ResultsPanel({ prediction }: ResultsPanelProps) {
    const isAttackMode = prediction.day_classification.includes("Attack");

    return (
        <div className="glass-panel rounded-2xl p-6 space-y-6 animate-fade-in">

            {/* ========== HEADER ========== */}
            <div className="text-center border-b border-white/10 pb-4">
                <h2 className="font-mono text-sm tracking-widest text-slate-500 uppercase">
                    HabitOS Performance Report
                </h2>
            </div>

            {/* ========== CLASSIFICATION ========== */}
            <div className="flex items-center justify-center gap-4">
                <div
                    className={`
            px-6 py-3 rounded-xl font-semibold text-lg
            ${isAttackMode
                            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                            : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        }
          `}
                >
                    {prediction.day_classification}
                </div>
            </div>

            {/* ========== PERSONA ========== */}
            <div className="text-center">
                <span className="text-sm text-slate-500 uppercase tracking-wider">Persona</span>
                <p className="text-xl font-semibold gradient-text mt-1">
                    {prediction.persona}
                </p>
            </div>

            {/* ========== RECOMMENDATIONS ========== */}
            <div className="space-y-3">
                <h3 className="font-mono text-sm text-slate-500 uppercase tracking-wider flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Personalized Directives
                </h3>

                <div className="space-y-2">
                    {prediction.recommendations.map((rec, index) => (
                        <div
                            key={index}
                            className="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border-l-2 border-blue-500/50"
                            style={{ animationDelay: `${index * 100}ms` }}
                        >
                            <span className="text-blue-400 mt-0.5">•</span>
                            <p className="text-sm text-slate-300 leading-relaxed">{rec}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* ========== FOOTER STATS ========== */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/10">
                <div className="text-center">
                    <span className="text-2xl font-bold neon-text-blue">
                        {Math.round(prediction.daily_score)}
                    </span>
                    <p className="text-xs text-slate-500 mt-1">Score</p>
                </div>
                <div className="text-center">
                    <span className="text-2xl font-bold text-slate-300">
                        {isAttackMode ? "⚡" : "🔋"}
                    </span>
                    <p className="text-xs text-slate-500 mt-1">Mode</p>
                </div>
                <div className="text-center">
                    <span className="text-2xl font-bold text-slate-300">
                        {prediction.recommendations.length}
                    </span>
                    <p className="text-xs text-slate-500 mt-1">Tips</p>
                </div>
            </div>
        </div>
    );
}
