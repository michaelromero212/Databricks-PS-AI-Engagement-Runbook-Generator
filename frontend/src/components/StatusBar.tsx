import React from 'react';
import { Activity, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { JOB_STATUS_COLORS } from '../lib/constants';

interface StatusBarProps {
    runId?: string;
    status: string;
    model: string;
    lastUpdated?: string;
}

export function StatusBar({ runId, status, model, lastUpdated }: StatusBarProps) {
    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'SUCCESS': return <CheckCircle className="h-4 w-4" />;
            case 'FAILED': return <XCircle className="h-4 w-4" />;
            case 'RUNNING': return <Activity className="h-4 w-4 animate-spin" />;
            default: return <AlertCircle className="h-4 w-4" />;
        }
    };

    const statusColor = JOB_STATUS_COLORS[status as keyof typeof JOB_STATUS_COLORS] || 'bg-gray-500';

    return (
        <div className="w-full bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-2 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                    <span className="font-semibold text-gray-500">Run ID:</span>
                    <span className="font-mono">{runId || 'N/A'}</span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="font-semibold text-gray-500">Status:</span>
                    <span className={`px-2 py-0.5 rounded-full text-white ${statusColor} flex items-center space-x-1`}>
                        {getStatusIcon(status)}
                        <span>{status}</span>
                    </span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="font-semibold text-gray-500">Model:</span>
                    <span>{model}</span>
                </div>
            </div>
            <div className="flex items-center space-x-2 text-gray-400">
                <Clock className="h-3 w-3" />
                <span>Last Updated: {lastUpdated || 'Never'}</span>
            </div>
        </div>
    );
}
