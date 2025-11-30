import React from 'react';
import { Play, RefreshCw, FileText } from 'lucide-react';

interface PipelineControlsProps {
    onRunPipeline: () => void;
    onRefresh: () => void;
    isRunning: boolean;
    hasResults: boolean;
}

export function PipelineControls({ onRunPipeline, onRefresh, isRunning, hasResults }: PipelineControlsProps) {
    return (
        <div className="flex flex-col space-y-2">
            <button
                onClick={onRunPipeline}
                disabled={isRunning}
                className={`flex items-center justify-center space-x-2 p-2 rounded-md text-white font-medium transition-colors
          ${isRunning
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-primary hover:bg-blue-700'
                    }`}
            >
                <Play className="h-4 w-4" />
                <span>{isRunning ? 'Pipeline Running...' : 'Run Pipeline'}</span>
            </button>

            <div className="flex space-x-2">
                <button
                    onClick={onRefresh}
                    className="flex-1 flex items-center justify-center space-x-2 p-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                    <RefreshCw className="h-4 w-4" />
                    <span>Refresh Status</span>
                </button>
            </div>
        </div>
    );
}
