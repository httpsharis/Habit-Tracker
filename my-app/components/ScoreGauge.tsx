"use client";

import { useEffect, useState } from 'react';

interface ScoreGaugeProps {
    score: number;
}

export default function ScoreGauge({ score }: ScoreGaugeProps) {
    const [animatedScore, setAnimatedScore] = useState(0);
    const [isAnimating, setIsAnimating] = useState(true);

    // Circle properties
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

    // Determine color based on score
    const getScoreColor = () => {
        if (score >= 75) return { class: 'gauge-excellent', color: 'var(--neon-green)' };
        if (score >= 50) return { class: 'gauge-good', color: 'var(--neon-blue)' };
        if (score >= 35) return { class: 'gauge-warning', color: 'var(--neon-amber)' };
        return { class: 'gauge-critical', color: 'var(--neon-red)' };
    };

    const scoreColor = getScoreColor();

    // Animate score on mount
    useEffect(() => {
        setIsAnimating(true);
        setAnimatedScore(0);

        const duration = 1500; // ms
        const steps = 60;
        const increment = score / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= score) {
                setAnimatedScore(score);
                setIsAnimating(false);
                clearInterval(timer);
            } else {
                setAnimatedScore(current);
            }
        }, duration / steps);

        return () => clearInterval(timer);
    }, [score]);

    return (
        <div className="relative w-44 h-44 animate-float">
            {/* SVG Gauge */}
            <svg
                width="176"
                height="176"
                viewBox="0 0 176 176"
                className="transform -rotate-90"
            >
                {/* Background Circle */}
                <circle
                    cx="88"
                    cy="88"
                    r={radius}
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="10"
                />

                {/* Animated Progress Circle */}
                <circle
                    cx="88"
                    cy="88"
                    r={radius}
                    fill="none"
                    stroke={scoreColor.color}
                    strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    className={`${scoreColor.class} transition-all duration-1000 ease-out`}
                />
            </svg>

            {/* Center Score Display */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span
                    className="text-5xl font-bold font-mono transition-colors duration-500"
                    style={{ color: scoreColor.color }}
                >
                    {Math.round(animatedScore)}
                </span>
                <span className="text-xs uppercase tracking-widest text-slate-500 mt-1">
                    Daily Score
                </span>
            </div>

            {/* Glow Effect */}
            <div
                className="absolute inset-0 rounded-full blur-2xl opacity-30 pointer-events-none"
                style={{ backgroundColor: scoreColor.color }}
            />
        </div>
    );
}
