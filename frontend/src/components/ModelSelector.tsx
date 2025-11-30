import React from 'react';
import { MODELS } from '../lib/constants';
import { Bot, Zap } from 'lucide-react';

interface ModelSelectorProps {
    selectedModel: string;
    onSelectModel: (modelId: string) => void;
}

export function ModelSelector({ selectedModel, onSelectModel }: ModelSelectorProps) {
    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Select AI Model</label>
            <div className="relative">
                <select
                    value={selectedModel}
                    onChange={(e) => onSelectModel(e.target.value)}
                    className="w-full p-2 pl-10 border rounded-md bg-white dark:bg-gray-800 dark:border-gray-700 focus:ring-2 focus:ring-primary focus:outline-none appearance-none"
                >
                    {MODELS.map((model) => (
                        <option key={model.id} value={model.id}>
                            {model.name} ({model.type})
                        </option>
                    ))}
                </select>
                <Bot className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
                <Zap className="h-3 w-3" />
                <span>
                    Speed: {MODELS.find(m => m.id === selectedModel)?.speed}
                </span>
            </div>
        </div>
    );
}
