"use client";

import { useUser } from '@/context/UserContext';
import Background from '@/components/Background';
import Header from '@/components/Header';
import Navigation from '@/components/Navigation';
import SessionCard from '@/components/SessionCard';

export default function HistoryPage() {
    const { user, sessions, isLoading, refreshSessions } = useUser();

    return (
        <main className="min-h-screen relative pb-24">
            <Background />
            <Header />
            <Navigation />

            <div className="max-w-4xl mx-auto px-6 pt-24">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold gradient-text mb-2">Session History</h1>
                    <p className="text-slate-500">
                        {user ? `Your past ${sessions.length} tracking sessions` : 'Sign in to view your history'}
                    </p>
                </div>

                {!user ? (
                    /* Not Logged In State */
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <div className="text-6xl mb-4">🔐</div>
                        <h2 className="text-xl font-semibold mb-2">Sign In Required</h2>
                        <p className="text-slate-500 mb-6">
                            Create an account to track your history and see personalized insights.
                        </p>
                    </div>
                ) : sessions.length === 0 ? (
                    /* No Sessions State */
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <div className="text-6xl mb-4">📭</div>
                        <h2 className="text-xl font-semibold mb-2">No Sessions Yet</h2>
                        <p className="text-slate-500">
                            Complete your first tracking session to see your history here.
                        </p>
                    </div>
                ) : (
                    /* Sessions List */
                    <div className="space-y-4">
                        {sessions.map((session, index) => (
                            <SessionCard
                                key={session.id}
                                session={session}
                                index={index}
                            />
                        ))}

                        {/* Load More Button */}
                        <button
                            onClick={refreshSessions}
                            disabled={isLoading}
                            className="w-full py-4 glass-panel glass-panel-hover rounded-xl text-slate-400 hover:text-white transition-colors disabled:opacity-50"
                        >
                            {isLoading ? 'Loading...' : '🔄 Refresh History'}
                        </button>
                    </div>
                )}
            </div>
        </main>
    );
}
