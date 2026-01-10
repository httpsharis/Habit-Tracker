"use client";

interface Session {
    id: number;
    sleep_hours: number;
    work_intensity: number;
    stress_level: number;
    mood_score: number;
    screen_time: number;
    hydration: number;
    daily_score: number;
    day_classification: string;
    persona: string;
    created_at: string;
}

interface SessionCardProps {
    session: Session;
    index: number;
}

export default function SessionCard({ session, index }: SessionCardProps) {
    const isAttackMode = session.day_classification.includes("Attack");
    const date = new Date(session.created_at);

    const formatDate = (d: Date) => {
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;

        return d.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
    };

    const getScoreColor = (score: number) => {
        if (score >= 75) return 'text-green-400';
        if (score >= 50) return 'text-blue-400';
        if (score >= 35) return 'text-amber-400';
        return 'text-red-400';
    };

    return (
        <div
            className="glass-panel rounded-xl p-5 hover:border-white/20 transition-all duration-300 animate-fade-in"
            style={{ animationDelay: `${index * 50}ms` }}
        >
            <div className="flex items-center justify-between">
                {/* Left Side - Score & Classification */}
                <div className="flex items-center gap-4">
                    {/* Score Circle */}
                    <div className={`
            w-14 h-14 rounded-full flex items-center justify-center font-bold text-lg font-mono
            ${isAttackMode ? 'bg-green-500/20' : 'bg-blue-500/20'}
          `}>
                        <span className={getScoreColor(session.daily_score)}>
                            {Math.round(session.daily_score)}
                        </span>
                    </div>

                    {/* Info */}
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className={`
                text-sm font-medium
                ${isAttackMode ? 'text-green-400' : 'text-blue-400'}
              `}>
                                {session.day_classification}
                            </span>
                            <span className="text-xs text-slate-600">•</span>
                            <span className="text-xs text-slate-500">{session.persona}</span>
                        </div>
                        <p className="text-xs text-slate-500">{formatDate(date)}</p>
                    </div>
                </div>

                {/* Right Side - Metrics Grid */}
                <div className="hidden sm:grid grid-cols-6 gap-4 text-center">
                    <MetricBadge icon="😴" value={session.sleep_hours} label="h" />
                    <MetricBadge icon="💼" value={session.work_intensity} />
                    <MetricBadge icon="😰" value={session.stress_level} />
                    <MetricBadge icon="😊" value={session.mood_score} />
                    <MetricBadge icon="📱" value={session.screen_time} label="h" />
                    <MetricBadge icon="💧" value={session.hydration} />
                </div>
            </div>

            {/* Mobile Metrics Row */}
            <div className="sm:hidden grid grid-cols-6 gap-2 mt-4 pt-4 border-t border-white/5">
                <MetricBadge icon="😴" value={session.sleep_hours} label="h" small />
                <MetricBadge icon="💼" value={session.work_intensity} small />
                <MetricBadge icon="😰" value={session.stress_level} small />
                <MetricBadge icon="😊" value={session.mood_score} small />
                <MetricBadge icon="📱" value={session.screen_time} label="h" small />
                <MetricBadge icon="💧" value={session.hydration} small />
            </div>
        </div>
    );
}

function MetricBadge({
    icon,
    value,
    label = "",
    small = false
}: {
    icon: string;
    value: number;
    label?: string;
    small?: boolean;
}) {
    return (
        <div className={`text-center ${small ? 'text-xs' : 'text-sm'}`}>
            <div className={small ? 'text-sm' : 'text-base'}>{icon}</div>
            <div className="font-mono text-slate-300">
                {typeof value === 'number' ? value.toFixed(1) : value}{label}
            </div>
        </div>
    );
}
