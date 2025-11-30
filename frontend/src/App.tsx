import React, { useState, useEffect } from 'react';
import { FileUploader } from './components/FileUploader';
import { ModelSelector } from './components/ModelSelector';
import { PipelineControls } from './components/PipelineControls';
import { StatusBar } from './components/StatusBar';
import { RunbookViewer } from './components/RunbookViewer';
import { DiffViewer } from './components/DiffViewer';
import { api } from './lib/api';
import { MODELS } from './lib/constants';

function App() {
    const [selectedModel, setSelectedModel] = useState(MODELS[0].id);
    const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
    const [runId, setRunId] = useState<string>('');
    const [jobStatus, setJobStatus] = useState<string>('IDLE');
    const [runbookContent, setRunbookContent] = useState<string>('');
    const [runbookMetadata, setRunbookMetadata] = useState<any>(null);
    const [showDiff, setShowDiff] = useState(false);
    const [lastUpdated, setLastUpdated] = useState<string>('');

    const handleUploadComplete = (filename: string) => {
        setUploadedFiles(prev => [...prev, filename]);
    };

    const handleRunPipeline = async () => {
        try {
            const res = await api.runPipeline(selectedModel, uploadedFiles);
            setRunId(res.run_id);
            setJobStatus(res.status);
            setLastUpdated(new Date().toLocaleTimeString());
        } catch (e) {
            console.error(e);
            alert('Failed to start pipeline');
        }
    };

    const handleRefresh = async () => {
        if (!runId) return;
        try {
            const res = await api.getJobStatus(runId);
            setJobStatus(res.status);
            setLastUpdated(new Date().toLocaleTimeString());

            if (res.status === 'SUCCESS' && !runbookContent) {
                await api.fetchRunbook(runId);
                const rb = await api.getLatestRunbook();
                setRunbookContent(rb.markdown_content);
                setRunbookMetadata(rb.metadata);
            }
        } catch (e) {
            console.error(e);
        }
    };

    // Poll for status if running
    useEffect(() => {
        let interval: any;
        if (jobStatus === 'RUNNING' || jobStatus === 'PENDING') {
            interval = setInterval(handleRefresh, 5000);
        }
        return () => clearInterval(interval);
    }, [jobStatus, runId]);

    return (
        <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between shadow-sm">
                <div className="flex items-center space-x-2">
                    <div className="h-8 w-8 bg-primary rounded-md flex items-center justify-center text-white font-bold">PS</div>
                    <h1 className="text-xl font-bold tracking-tight">AI Engagement Runbook Generator</h1>
                </div>
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => setShowDiff(!showDiff)}
                        className="text-sm font-medium text-primary hover:underline"
                    >
                        {showDiff ? 'View Runbook' : 'Compare Versions'}
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Sidebar */}
                <aside className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col p-4 space-y-6 overflow-y-auto">
                    <section>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">1. Ingestion</h3>
                        <FileUploader onUploadComplete={handleUploadComplete} />
                    </section>

                    <section>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">2. Configuration</h3>
                        <ModelSelector selectedModel={selectedModel} onSelectModel={setSelectedModel} />
                    </section>

                    <section>
                        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">3. Execution</h3>
                        <PipelineControls
                            onRunPipeline={handleRunPipeline}
                            onRefresh={handleRefresh}
                            isRunning={jobStatus === 'RUNNING' || jobStatus === 'PENDING'}
                            hasResults={!!runbookContent}
                        />
                    </section>
                </aside>

                {/* Main View Area */}
                <main className="flex-1 bg-white dark:bg-gray-900 overflow-hidden relative">
                    {showDiff ? (
                        <DiffViewer oldContent="# Old Version..." newContent={runbookContent || "# New Version..."} />
                    ) : (
                        <RunbookViewer content={runbookContent} metadata={runbookMetadata} />
                    )}
                </main>
            </div>

            {/* Status Bar */}
            <StatusBar
                runId={runId}
                status={jobStatus}
                model={MODELS.find(m => m.id === selectedModel)?.name || selectedModel}
                lastUpdated={lastUpdated}
            />
        </div>
    );
}

export default App;
