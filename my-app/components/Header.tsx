"use client";

import { useUser } from '@/context/UserContext';
import { useState } from 'react';

export default function Header() {
    const { user, stats, login, logout, isLoading } = useUser();
    const [username, setUsername] = useState("");
    const [showLogin, setShowLogin] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (username.trim()) {
            await login(username.trim());
            setShowLogin(false);
            setUsername("");
        }
    };

    return (
        <header className="fixed top-0 left-0 right-0 z-50 p-4">
            <div className="max-w-6xl mx-auto flex items-center justify-between">

                {/* Logo */}
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-lg">
                        H
                    </div>
                    <div>
                        <h1 className="font-bold text-lg">HabitOS</h1>
                        <p className="text-xs text-slate-500">Performance Tracking</p>
                    </div>
                </div>

                {/* User Section */}
                <div className="flex items-center gap-4">
                    {user ? (
                        <>
                            {/* Stats Badge */}
                            {stats && stats.total_sessions > 0 && (
                                <div className="hidden sm:flex items-center gap-2 glass-panel px-4 py-2 rounded-lg text-sm">
                                    <span className="text-slate-400">Sessions:</span>
                                    <span className="font-mono text-blue-400">{stats.total_sessions}</span>
                                    <span className="text-slate-600">|</span>
                                    <span className="text-slate-400">Avg:</span>
                                    <span className="font-mono text-green-400">{stats.avg_daily_score}</span>
                                </div>
                            )}

                            {/* User Info */}
                            <div className="flex items-center gap-3">
                                <div className="text-right hidden sm:block">
                                    <p className="text-sm font-medium">{user.username}</p>
                                    <p className="text-xs text-slate-500">Member</p>
                                </div>
                                <button
                                    onClick={logout}
                                    className="p-2 rounded-lg hover:bg-white/10 transition-colors text-slate-400 hover:text-white"
                                    title="Logout"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                    </svg>
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            {showLogin ? (
                                <form onSubmit={handleLogin} className="flex items-center gap-2">
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="Enter username..."
                                        className="bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 w-40"
                                        autoFocus
                                    />
                                    <button
                                        type="submit"
                                        disabled={isLoading}
                                        className="px-4 py-2 bg-blue-500/20 text-blue-400 rounded-lg text-sm hover:bg-blue-500/30 transition-colors disabled:opacity-50"
                                    >
                                        {isLoading ? "..." : "Go"}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setShowLogin(false)}
                                        className="p-2 text-slate-500 hover:text-white"
                                    >
                                        ✕
                                    </button>
                                </form>
                            ) : (
                                <button
                                    onClick={() => setShowLogin(true)}
                                    className="px-4 py-2 glass-panel glass-panel-hover rounded-lg text-sm flex items-center gap-2"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                    </svg>
                                    Sign In
                                </button>
                            )}
                        </>
                    )}
                </div>
            </div>
        </header>
    );
}
