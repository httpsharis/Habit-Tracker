"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
    { href: '/', label: 'Track', icon: '🎯' },
    { href: '/history', label: 'History', icon: '📊' },
    { href: '/charts', label: 'Charts', icon: '📈' },
    { href: '/insights', label: 'Insights', icon: '💡' },
];

export default function Navigation() {
    const pathname = usePathname();

    return (
        <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
            <div className="glass-panel rounded-2xl px-2 py-2 flex items-center gap-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`
                flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-300
                ${isActive
                                    ? 'bg-blue-500/20 text-blue-400'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }
              `}
                        >
                            <span className="text-lg">{item.icon}</span>
                            <span className="text-sm font-medium hidden sm:block">{item.label}</span>
                        </Link>
                    );
                })}
            </div>
        </nav>
    );
}
