"use client";

import { useEffect, useState } from 'react';

export default function Background() {
    const [mousePos, setMousePos] = useState({ x: 50, y: 50 });

    // Track mouse for subtle parallax effect
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePos({
                x: (e.clientX / window.innerWidth) * 100,
                y: (e.clientY / window.innerHeight) * 100
            });
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <div className="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">

            {/* ========== 1. ANIMATED GRID ========== */}
            <div
                className="absolute w-[200%] h-[200%] opacity-[0.08]"
                style={{
                    backgroundImage: `
            linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
          `,
                    backgroundSize: '50px 50px',
                    animation: 'gridMove 25s linear infinite',
                    transform: 'perspective(500px) rotateX(60deg)',
                    transformOrigin: 'center top'
                }}
            />

            {/* ========== 2. PRIMARY GLOW ORB ========== */}
            <div
                className="absolute w-[700px] h-[700px] rounded-full"
                style={{
                    background: 'radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%)',
                    top: `${50 + (mousePos.y - 50) * 0.02}%`,
                    left: `${50 + (mousePos.x - 50) * 0.02}%`,
                    transform: 'translate(-50%, -50%)',
                    animation: 'breathe 8s ease-in-out infinite',
                }}
            />

            {/* ========== 3. SECONDARY ACCENT ORB ========== */}
            <div
                className="absolute w-[400px] h-[400px] rounded-full"
                style={{
                    background: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%)',
                    top: `${30 + (mousePos.y - 50) * -0.03}%`,
                    right: `${10 + (mousePos.x - 50) * -0.02}%`,
                    animation: 'breathe 10s ease-in-out infinite',
                    animationDelay: '-5s'
                }}
            />

            {/* ========== 4. TERTIARY GREEN ORB ========== */}
            <div
                className="absolute w-[300px] h-[300px] rounded-full"
                style={{
                    background: 'radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)',
                    bottom: '20%',
                    left: '15%',
                    animation: 'breathe 12s ease-in-out infinite',
                    animationDelay: '-3s'
                }}
            />

            {/* ========== 5. NOISE OVERLAY ========== */}
            <div
                className="absolute inset-0 opacity-[0.02]"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
                }}
            />

            {/* ========== 6. VIGNETTE EFFECT ========== */}
            <div
                className="absolute inset-0"
                style={{
                    background: 'radial-gradient(circle at 50% 50%, transparent 0%, rgba(5, 5, 5, 0.5) 100%)'
                }}
            />

            {/* ========== 7. TOP GRADIENT FADE ========== */}
            <div
                className="absolute top-0 left-0 right-0 h-32"
                style={{
                    background: 'linear-gradient(to bottom, rgba(5, 5, 5, 0.8), transparent)'
                }}
            />

            {/* ========== 8. BOTTOM GRADIENT FADE ========== */}
            <div
                className="absolute bottom-0 left-0 right-0 h-32"
                style={{
                    background: 'linear-gradient(to top, rgba(5, 5, 5, 0.9), transparent)'
                }}
            />
        </div>
    );
}