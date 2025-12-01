import React from 'react';
import { LucideIcon } from 'lucide-react';

interface ScenarioCardProps {
    icon: LucideIcon;
    iconColor: string;
    iconBgColor: string;
    label: string;
    title: string;
    description: string;
    hoverBorderColor: string;
    onClick: () => void;
}

export function ScenarioCard({
    icon: Icon,
    iconColor,
    iconBgColor,
    label,
    title,
    description,
    hoverBorderColor,
    onClick
}: ScenarioCardProps) {
    // Map hover border colors to static Tailwind classes
    const borderColorClass = {
        'blue-400': 'hover:border-blue-400',
        'purple-400': 'hover:border-purple-400',
        'orange-400': 'hover:border-orange-400',
        'green-400': 'hover:border-green-400',
    }[hoverBorderColor] || 'hover:border-gray-400';

    return (
        <div
            onClick={onClick}
            className={`bg-white dark:bg-gray-800 p-6 rounded-xl cursor-pointer border border-gray-200 dark:border-gray-700 ${borderColorClass} transition-all group shadow-sm hover:shadow-md relative z-10`}
        >
            <div className="flex justify-between items-start mb-4">
                <div className={`p-2 ${iconBgColor} rounded-lg group-hover:opacity-90 transition-opacity`}>
                    <Icon className={`w-6 h-6 ${iconColor}`} />
                </div>
                <span className="text-xs font-medium text-gray-400">{label}</span>
            </div>
            <h4 className="font-semibold text-gray-900 dark:text-gray-100">{title}</h4>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{description}</p>
        </div>
    );
}
