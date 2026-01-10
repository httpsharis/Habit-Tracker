"use client";

interface ChartData {
    index: number;
    date: string;
    [key: string]: number | string;
}

interface MetricChartProps {
    data: ChartData[];
    dataKey: string;
    color: string;
    label: string;
    max: number;
    invertColor?: boolean;
}

export default function MetricChart({
    data,
    dataKey,
    color,
    label,
    max,
    invertColor = false
}: MetricChartProps) {
    if (data.length === 0) {
        return (
            <div className="h-40 flex items-center justify-center text-slate-500">
                No data available
            </div>
        );
    }

    const chartHeight = 160;

    return (
        <div className="relative">
            {/* Y-axis labels */}
            <div className="absolute left-0 top-0 bottom-8 w-8 flex flex-col justify-between text-xs text-slate-600 font-mono">
                <span>{max}</span>
                <span>{max / 2}</span>
                <span>0</span>
            </div>

            {/* Chart Area */}
            <div className="ml-10 mr-2">
                {/* Grid Lines */}
                <div className="absolute inset-0 ml-10 mr-2" style={{ top: 0, bottom: 32 }}>
                    <div className="absolute w-full border-t border-white/5" style={{ top: '0%' }} />
                    <div className="absolute w-full border-t border-white/5" style={{ top: '50%' }} />
                    <div className="absolute w-full border-t border-white/5" style={{ top: '100%' }} />
                </div>

                {/* Bars */}
                <div
                    className="flex items-end justify-between gap-1"
                    style={{ height: chartHeight }}
                >
                    {data.map((item, index) => {
                        const value = Number(item[dataKey]) || 0;
                        const heightPercent = Math.min((value / max) * 100, 100);

                        // Color logic for inverted metrics (like stress)
                        let barColor = color;
                        if (invertColor) {
                            const ratio = value / max;
                            if (ratio > 0.7) barColor = '#ef4444';
                            else if (ratio > 0.5) barColor = '#f59e0b';
                            else barColor = '#10b981';
                        }

                        return (
                            <div
                                key={index}
                                className="flex-1 flex flex-col items-center group"
                            >
                                {/* Tooltip */}
                                <div className="relative mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-black/80 rounded text-xs whitespace-nowrap z-10">
                                        {value.toFixed(1)} {label}
                                        <div className="text-slate-500">{item.date}</div>
                                    </div>
                                </div>

                                {/* Bar */}
                                <div
                                    className="w-full max-w-[30px] rounded-t transition-all duration-300 hover:opacity-80 cursor-pointer"
                                    style={{
                                        height: `${heightPercent}%`,
                                        backgroundColor: barColor,
                                        minHeight: value > 0 ? '4px' : '0px',
                                        boxShadow: `0 0 10px ${barColor}40`
                                    }}
                                />
                            </div>
                        );
                    })}
                </div>

                {/* X-axis labels */}
                <div className="flex justify-between mt-2 text-xs text-slate-600">
                    {data.length <= 7 ? (
                        data.map((item, i) => (
                            <span key={i} className="flex-1 text-center truncate">{item.date}</span>
                        ))
                    ) : (
                        <>
                            <span>{data[0]?.date}</span>
                            <span className="text-slate-500">{data.length} sessions</span>
                            <span>{data[data.length - 1]?.date}</span>
                        </>
                    )}
                </div>
            </div>

            {/* Current Value Badge */}
            {data.length > 0 && (
                <div
                    className="absolute top-0 right-0 px-3 py-1 rounded-lg text-sm font-mono"
                    style={{ backgroundColor: `${color}20`, color }}
                >
                    Latest: {Number(data[data.length - 1]?.[dataKey]).toFixed(1)}
                </div>
            )}
        </div>
    );
}
