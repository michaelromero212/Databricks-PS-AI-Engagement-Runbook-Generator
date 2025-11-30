import React from 'react';
import Markdown from 'react-markdown';
import { Download, Copy } from 'lucide-react';

interface RunbookViewerProps {
    content: string;
    metadata?: any;
}

export function RunbookViewer({ content, metadata }: RunbookViewerProps) {
    if (!content) {
        return (
            <div className="flex items-center justify-center h-full text-gray-400">
                No runbook generated yet. Run the pipeline to generate one.
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center justify-between p-4 border-b bg-gray-50 dark:bg-gray-900">
                <h2 className="font-semibold text-lg">Generated Runbook</h2>
                <div className="flex space-x-2">
                    <button className="p-2 hover:bg-gray-200 rounded-full" title="Copy">
                        <Copy className="h-4 w-4" />
                    </button>
                    <button className="p-2 hover:bg-gray-200 rounded-full" title="Download">
                        <Download className="h-4 w-4" />
                    </button>
                </div>
            </div>
            <div className="flex-1 overflow-auto p-8 prose dark:prose-invert max-w-none">
                <Markdown>{content}</Markdown>
            </div>
            {metadata && (
                <div className="p-2 bg-gray-100 dark:bg-gray-800 text-xs text-gray-500 border-t">
                    Metadata: {JSON.stringify(metadata)}
                </div>
            )}
        </div>
    );
}
