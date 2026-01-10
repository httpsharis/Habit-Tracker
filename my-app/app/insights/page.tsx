"use client";

import { useUser } from '@/context/UserContext';
import Background from '@/components/Background';
import Header from '@/components/Header';
import Navigation from '@/components/Navigation';

interface Insight {
    icon: string;
    type: 'success' | 'warning' | 'critical';
    title: string;
    description: string;
    action: string;
}

export default function InsightsPage() {
    const { user, stats, sessions } = useUser();

    // Calculate insights from data
    const getInsights = (): Insight[] => {
        if (!stats || sessions.length < 3) return [];

        const insights: Insight[] = [];

        // Sleep insight
        if (stats.avg_sleep < 6) {
            insights.push({
                icon: '😴',
                type: 'warning',
                title: 'Sleep Deficit Detected',
                description: `Your average sleep is ${stats.avg_sleep.toFixed(1)} hours. Consider aiming for 7-9 hours for optimal performance.`,
                action: 'Set a consistent bedtime 30 minutes earlier.'
            });
        } else if (stats.avg_sleep >= 7) {
            insights.push({
                icon: '🌙',
                type: 'success',
                title: 'Great Sleep Habits',
                description: `You're averaging ${stats.avg_sleep.toFixed(1)} hours of sleep, which is in the healthy range.`,
                action: 'Maintain your current sleep schedule.'
            });
        }

        // Stress insight
        if (stats.avg_stress >= 7) {
            insights.push({
                icon: '🔴',
                type: 'critical',
                title: 'High Stress Alert',
                description: `Your average stress level is ${stats.avg_stress.toFixed(1)}/10. This may be affecting your overall wellbeing.`,
                action: 'Try box breathing (4-4-4-4) or a 10-minute walk.'
            });
        } else if (stats.avg_stress <= 4) {
            insights.push({
                icon: '😌',
                type: 'success',
                title: 'Stress Under Control',
                description: `Your stress levels are well-managed at ${stats.avg_stress.toFixed(1)}/10.`,
                action: 'Keep up your stress management practices.'
            });
        }

        // Hydration insight
        if (stats.avg_hydration < 6) {
            insights.push({
                icon: '💧',
                type: 'warning',
                title: 'Hydration Needs Attention',
                description: `You're averaging only ${stats.avg_hydration.toFixed(1)} glasses of water. Aim for 8+ for optimal function.`,
                action: 'Set hourly reminders to drink water.'
            });
        }

        // Screen time insight
        if (stats.avg_screen_time > 8) {
            insights.push({
                icon: '📱',
                type: 'warning',
                title: 'High Screen Time',
                description: `You're spending ${stats.avg_screen_time.toFixed(1)} hours on screens daily.`,
                action: 'Use the 20-20-20 rule: every 20 mins, look 20ft away for 20 seconds.'
            });
        }

        // Performance trend
        if (stats.score_trend?.includes('↑')) {
            insights.push({
                icon: '📈',
                type: 'success',
                title: 'Performance Improving',
                description: 'Your recent scores are trending upward. Great progress!',
                action: 'Identify what\'s working and double down.'
            });
        } else if (stats.score_trend?.includes('↓')) {
            insights.push({
                icon: '📉',
                type: 'warning',
                title: 'Performance Declining',
                description: 'Your recent scores are below your average.',
                action: 'Review your sleep and stress levels for patterns.'
            });
        }

        // Mood insight
        if (stats.avg_mood <= 4) {
            insights.push({
                icon: '🌅',
                type: 'warning',
                title: 'Mood Optimization Needed',
                description: `Your average mood is ${stats.avg_mood.toFixed(1)}/10. Consider mood-boosting activities.`,
                action: 'Try sunlight exposure, exercise, or connecting with friends.'
            });
        }

        // Sessions consistency
        if (sessions.length >= 7) {
            insights.push({
                icon: '🏆',
                type: 'success',
                title: 'Consistent Tracking',
                description: `You've logged ${sessions.length} sessions. Consistency is key to improvement!`,
                action: 'Keep up your daily tracking habit.'
            });
        }

        return insights;
    };

    const insights = getInsights();

    return (
        <main className="min-h-screen relative pb-24">
            <Background />
            <Header />
            <Navigation />

            <div className="max-w-4xl mx-auto px-6 pt-24">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold gradient-text mb-2">AI Insights</h1>
                    <p className="text-slate-500">
                        {user ? 'Personalized recommendations based on your data' : 'Sign in to view your insights'}
                    </p>
                </div>

                {!user ? (
                    /* Not Logged In State */
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <div className="text-6xl mb-4">💡</div>
                        <h2 className="text-xl font-semibold mb-2">Sign In Required</h2>
                        <p className="text-slate-500">
                            Create an account to get personalized insights.
                        </p>
                    </div>
                ) : sessions.length < 3 ? (
                    /* Not Enough Data State */
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <div className="text-6xl mb-4">🔮</div>
                        <h2 className="text-xl font-semibold mb-2">Need More Data</h2>
                        <p className="text-slate-500">
                            Complete at least 3 sessions to generate personalized insights.
                        </p>
                        <div className="mt-6 flex justify-center gap-2">
                            {[1, 2, 3].map((i) => (
                                <div
                                    key={i}
                                    className={`w-10 h-10 rounded-full flex items-center justify-center ${sessions.length >= i
                                        ? 'bg-green-500/20 text-green-400'
                                        : 'bg-white/5 text-slate-600'
                                        }`}
                                >
                                    {sessions.length >= i ? '✓' : i}
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    /* Insights Grid */
                    <div className="space-y-4">
                        {insights.length === 0 ? (
                            <div className="glass-panel rounded-2xl p-12 text-center">
                                <div className="text-6xl mb-4">✨</div>
                                <h2 className="text-xl font-semibold mb-2">All Systems Normal</h2>
                                <p className="text-slate-500">
                                    Your metrics look balanced. Keep up the great work!
                                </p>
                            </div>
                        ) : (
                            insights.map((insight, index) => (
                                <InsightCard key={index} insight={insight} index={index} />
                            ))
                        )}

                        {/* Quick Stats */}
                        {stats && (
                            <div className="glass-panel rounded-2xl p-6 mt-8">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span>📊</span> Quick Summary
                                </h3>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <QuickStat
                                        label="Total Sessions"
                                        value={stats.total_sessions.toString()}
                                        trend={null}
                                    />
                                    <QuickStat
                                        label="Avg Score"
                                        value={`${stats.avg_daily_score.toFixed(0)}/100`}
                                        trend={stats.score_trend || null}
                                    />
                                    <QuickStat
                                        label="Avg Sleep"
                                        value={`${stats.avg_sleep.toFixed(1)}h`}
                                        trend={stats.sleep_trend || null}
                                    />
                                    <QuickStat
                                        label="Avg Mood"
                                        value={`${stats.avg_mood.toFixed(1)}/10`}
                                        trend={stats.mood_trend || null}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </main>
    );
}

function InsightCard({ insight, index }: { insight: Insight; index: number }) {
    const typeStyles = {
        success: 'border-l-green-500 bg-green-500/5',
        warning: 'border-l-amber-500 bg-amber-500/5',
        critical: 'border-l-red-500 bg-red-500/5'
    };

    return (
        <div
            className={`
        glass-panel rounded-xl p-6 border-l-4 
        ${typeStyles[insight.type]}
        animate-fade-in
      `}
            style={{ animationDelay: `${index * 100}ms` }}
        >
            <div className="flex items-start gap-4">
                <span className="text-3xl">{insight.icon}</span>
                <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-1">{insight.title}</h3>
                    <p className="text-slate-400 text-sm mb-3">{insight.description}</p>
                    <div className="flex items-center gap-2 text-sm">
                        <span className="text-blue-400">💡</span>
                        <span className="text-slate-300">{insight.action}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

function QuickStat({ label, value, trend }: { label: string; value: string; trend: string | null }) {
    return (
        <div className="text-center p-3 bg-white/5 rounded-xl">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
            <p className="text-xl font-bold font-mono text-white">{value}</p>
            {trend && (
                <p className={`text-xs mt-1 ${trend.includes('↑') ? 'text-green-400' :
                    trend.includes('↓') ? 'text-red-400' : 'text-slate-500'
                    }`}>
                    {trend}
                </p>
            )}
        </div>
    );
}
