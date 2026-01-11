"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface User {
    id: number;
    username: string;
    created_at: string;
}

interface UserStats {
    user_id: number;
    total_sessions: number;
    avg_sleep: number;
    avg_work_intensity: number;
    avg_stress: number;
    avg_mood: number;
    avg_screen_time: number;
    avg_hydration: number;
    avg_daily_score: number;
    recent_avg_daily_score?: number;
    sleep_trend?: string;
    stress_trend?: string;
    mood_trend?: string;
    score_trend?: string;
}

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

interface UserContextType {
    user: User | null;
    stats: UserStats | null;
    sessions: Session[];
    isLoading: boolean;
    error: string | null;
    login: (username: string) => Promise<void>;
    logout: () => void;
    refreshStats: () => Promise<void>;
    refreshSessions: () => Promise<void>;
}

// ============================================================================
// CONTEXT
// ============================================================================

const UserContext = createContext<UserContextType | undefined>(undefined);

// Use environment variable for API URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// ============================================================================
// PROVIDER
// ============================================================================

export function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [stats, setStats] = useState<UserStats | null>(null);
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Check for existing session on mount
    useEffect(() => {
        const validateAndLoadUser = async () => {
            const savedUser = localStorage.getItem('habitos_user');
            if (savedUser) {
                const parsed = JSON.parse(savedUser);
                
                // Verify user still exists in database
                try {
                    const res = await fetch(`${API_BASE}/user/${parsed.id}`);
                    if (res.ok) {
                        setUser(parsed);
                        fetchStats(parsed.id);
                        fetchSessions(parsed.id);
                    } else {
                        // User doesn't exist in DB anymore - clear local storage
                        console.warn("User not found in database, clearing session");
                        localStorage.removeItem('habitos_user');
                        setUser(null);
                    }
                } catch (err) {
                    console.warn("Could not validate user:", err);
                }
            }
        };
        
        validateAndLoadUser();
    }, []);

    // Fetch user stats
    const fetchStats = async (userId: number) => {
        try {
            const res = await fetch(`${API_BASE}/user/${userId}/stats`);
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            } else {
                console.warn("Stats endpoint returned:", res.status);
            }
        } catch (err) {
            // Backend might not be running - this is okay during development
            console.warn("Could not fetch stats - is the backend running?", err);
        }
    };

    // Fetch user sessions
    const fetchSessions = async (userId: number) => {
        try {
            const res = await fetch(`${API_BASE}/user/${userId}/history?limit=10`);
            if (res.ok) {
                const data = await res.json();
                setSessions(data.sessions || []);
            } else {
                console.warn("History endpoint returned:", res.status);
            }
        } catch (err) {
            console.warn("Could not fetch sessions - is the backend running?", err);
        }
    };

    // Login / Register
    const login = async (username: string) => {
        setIsLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE}/user`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username })
            });

            if (!res.ok) throw new Error("Failed to login");

            const userData: User = await res.json();
            setUser(userData);
            localStorage.setItem('habitos_user', JSON.stringify(userData));

            // Fetch stats and sessions
            await fetchStats(userData.id);
            await fetchSessions(userData.id);

        } catch (err: any) {
            setError(err.message || "Login failed");
        } finally {
            setIsLoading(false);
        }
    };

    // Logout
    const logout = () => {
        setUser(null);
        setStats(null);
        setSessions([]);
        localStorage.removeItem('habitos_user');
    };

    // Refresh stats
    const refreshStats = async () => {
        if (user) await fetchStats(user.id);
    };

    // Refresh sessions
    const refreshSessions = async () => {
        if (user) await fetchSessions(user.id);
    };

    return (
        <UserContext.Provider value={{
            user,
            stats,
            sessions,
            isLoading,
            error,
            login,
            logout,
            refreshStats,
            refreshSessions
        }}>
            {children}
        </UserContext.Provider>
    );
}

// ============================================================================
// HOOK
// ============================================================================

export function useUser() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}
