"use client";

import { useUser } from '@/context/UserContext';
import Background from '@/components/Background';
import Header from '@/components/Header';
import Navigation from '@/components/Navigation';
import MetricChart from '@/components/MetricChart';

export default function ChartsPage() {
    const { user, sessions, stats } = useUser();

    // Transform sessions into chart data
    const chartData = sessions
        .slice()
        .reverse()
        .map((s, i) => ({
            index: i + 1,
            date: new Date(s.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            score: s.daily_score,
            sleep: s.sleep_hours,
            stress: s.stress_level,
            mood: s.mood_score,
            screen: s.screen_time,
            hydration: s.hydration,
            work: s.work_intensity
        }));

    return (
        <main className="min-h-screen relative pb-24">
            <Background />
            <Header />
            <Navigation />

            <div className="max-w-6xl mx-auto px-6 pt-24">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold gradient-text mb-2">Performance Charts</h1>
                    <p className="text-slate-500">
                        {user ? 'Visualize your trends over time' : 'Sign in to view your charts'}
                    </p>
                </div>

                {!user ? (
                    /* Not Logged In State */
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <div className="text-6xl mb-4">📊</div>
                        <h2 className="text-xl font-semibold mb-2">Sign In Required</h2>
                        <p className="text-slate-500">
                            Create an account to see your performance charts.
                        </p>
                    </div>
                ) : sessions.length < 2 ? (
                    /* Not Enough Data State */
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <div className="text-6xl mb-4">📈</div>
                        <h2 className="text-xl font-semibold mb-2">Need More Data</h2>
                        <p className="text-slate-500">
                            Complete at least 2 sessions to see your trends visualized.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {/* Daily Score Chart */}
                        <div className="glass-panel rounded-2xl p-6">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <span>📊</span> Daily Score Trend
                            </h3>
                            <MetricChart
                                data={chartData}
                                dataKey="score"
                                color="#3b82f6"
                                label="Score"
                                max={100}
                            />
                        </div>

                        {/* Two Column Charts */}
                        <div className="grid md:grid-cols-2 gap-6">
                            {/* Sleep Chart */}
                            <div className="glass-panel rounded-2xl p-6">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span>😴</span> Sleep Hours
                                </h3>
                                <MetricChart
                                    data={chartData}
                                    dataKey="sleep"
                                    color="#8b5cf6"
                                    label="Hours"
                                    max={12}
                                />
                            </div>

                            {/* Stress Chart */}
                            <div className="glass-panel rounded-2xl p-6">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span>😰</span> Stress Level
                                </h3>
                                <MetricChart
                                    data={chartData}
                                    dataKey="stress"
                                    color="#ef4444"
                                    label="Level"
                                    max={10}
                                    invertColor
                                />
                            </div>

                            {/* Mood Chart */}
                            <div className="glass-panel rounded-2xl p-6">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span>😊</span> Mood Score
                                </h3>
                                <MetricChart
                                    data={chartData}
                                    dataKey="mood"
                                    color="#10b981"
                                    label="Score"
                                    max={10}
                                />
                            </div>

                            {/* Hydration Chart */}
                            <div className="glass-panel rounded-2xl p-6">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span>💧</span> Hydration
                                </h3>
                                <MetricChart
                                    data={chartData}
                                    dataKey="hydration"
                                    color="#06b6d4"
                                    label="Glasses"
                                    max={12}
                                />
                            </div>
                        </div>

                        {/* Averages Summary */}
                        {stats && (
                            <div className="glass-panel rounded-2xl p-6">
                                <h3 className="text-lg font-semibold mb-4">📈 Your Averages</h3>
                                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-4">
                                    <StatBox label="Score" value={stats.avg_daily_score} suffix="/100" />
                                    <StatBox label="Sleep" value={stats.avg_sleep} suffix="h" />
                                    <StatBox label="Work" value={stats.avg_work_intensity} suffix="/10" />
                                    <StatBox label="Stress" value={stats.avg_stress} suffix="/10" />
                                    <StatBox label="Mood" value={stats.avg_mood} suffix="/10" />
                                    <StatBox label="Screen" value={stats.avg_screen_time} suffix="h" />
                                    <StatBox label="Water" value={stats.avg_hydration} suffix="g" />
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </main>
    );
}

function StatBox({ label, value, suffix }: { label: string; value: number; suffix: string }) {
    return (
        <div className="text-center p-3 bg-white/5 rounded-xl">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
            <p className="text-lg font-bold font-mono text-blue-400">
                {value?.toFixed(1)}{suffix}
            </p>
        </div>
    );
}
