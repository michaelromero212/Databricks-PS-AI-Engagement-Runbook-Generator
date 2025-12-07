import React, { useState, useEffect } from 'react';
import { ScenarioSelector } from './components/ScenarioSelector';
import { ModelSelector } from './components/ModelSelector';
import { PipelineControls } from './components/PipelineControls';
import { StatusBar } from './components/StatusBar';
import { RunbookViewer } from './components/RunbookViewer';
import { api } from './lib/api';
import { MODELS } from './lib/constants';
import { AlertCircle, X } from 'lucide-react';

function App() {
    const [selectedModel, setSelectedModel] = useState(MODELS[0].id);
    const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
    const [runId, setRunId] = useState<string>('');
    const [jobStatus, setJobStatus] = useState<string>('IDLE');
    const [runbookContent, setRunbookContent] = useState<string>('');
    const [runbookMetadata, setRunbookMetadata] = useState<any>(null);
    const [lastUpdated, setLastUpdated] = useState<string>('');
    const [error, setError] = useState<string | null>(null);

    const handleFilesLoaded = (files: string[]) => {
        setUploadedFiles(files);
        setError(null); // Clear any previous errors
    };

    const dismissError = () => setError(null);

    const handleRunPipeline = async () => {
        try {
            setError(null);
            const res = await api.runPipeline(selectedModel, uploadedFiles);
            setRunId(res.run_id);
            setJobStatus(res.status);
            setLastUpdated(new Date().toLocaleTimeString());
        } catch (e) {
            console.error(e);
            setError('Failed to start pipeline. Please check your Databricks connection and try again.');
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
                const rb = await api.getRunbook(runId);
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
        <div className="h-screen flex overflow-hidden bg-gray-50 dark:bg-gray-900">
            {/* Dark Sidebar */}
            <aside className="w-64 bg-[#1B3139] text-white flex flex-col flex-shrink-0">
                <div className="p-6 border-b border-slate-700">
                    <h1 className="font-bold text-lg tracking-tight">PS AI Runbook</h1>
                    <p className="text-xs text-slate-400 mt-1">Engagement Generator</p>
                </div>

                <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
                    <div className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Pipeline Status</div>
                    <div className="space-y-4 px-4">
                        <div className={`flex items-center space-x-3 text-sm ${jobStatus !== 'IDLE' ? 'text-white' : 'text-slate-400'}`}>
                            <div className={`w-2 h-2 rounded-full ${jobStatus !== 'IDLE' ? 'bg-green-500' : 'bg-slate-600'}`}></div>
                            <span>Ingestion</span>
                        </div>
                        <div className={`flex items-center space-x-3 text-sm ${jobStatus === 'RUNNING' || jobStatus === 'SUCCESS' ? 'text-white' : 'text-slate-400'}`}>
                            <div className={`w-2 h-2 rounded-full ${jobStatus === 'RUNNING' ? 'bg-blue-500 animate-pulse' : jobStatus === 'SUCCESS' ? 'bg-green-500' : 'bg-slate-600'}`}></div>
                            <span>NLP Analysis</span>
                        </div>
                        <div className={`flex items-center space-x-3 text-sm ${jobStatus === 'SUCCESS' ? 'text-white' : 'text-slate-400'}`}>
                            <div className={`w-2 h-2 rounded-full ${jobStatus === 'SUCCESS' ? 'bg-green-500' : 'bg-slate-600'}`}></div>
                            <span>Embeddings</span>
                        </div>
                        <div className={`flex items-center space-x-3 text-sm ${jobStatus === 'SUCCESS' ? 'text-white' : 'text-slate-400'}`}>
                            <div className={`w-2 h-2 rounded-full ${jobStatus === 'SUCCESS' ? 'bg-green-500' : 'bg-slate-600'}`}></div>
                            <span>Generation</span>
                        </div>
                    </div>
                </nav>

                <div className="p-4 border-t border-slate-700">
                    <div className="text-xs text-slate-400">Connected to Databricks</div>
                    <div className="flex items-center mt-2 space-x-2">
                        <div className="w-2 h-2 rounded-full bg-green-500"></div>
                        <span className="text-sm font-medium">Online</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 h-16 flex items-center justify-between px-8 shadow-sm">
                    <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">New Engagement</h2>
                    <div className="flex items-center space-x-4">
                        <ModelSelector selectedModel={selectedModel} onSelectModel={setSelectedModel} />
                        <button
                            onClick={handleRunPipeline}
                            disabled={uploadedFiles.length === 0 || jobStatus === 'RUNNING' || jobStatus === 'PENDING'}
                            className="bg-[#FF3621] hover:bg-[#D92B19] text-white px-6 py-2 rounded-md font-medium transition-colors shadow-sm flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>Generate Runbook</span>
                        </button>
                    </div>
                </header>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8">
                    {/* Error Banner */}
                    {error && (
                        <div
                            role="alert"
                            className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded-r-lg flex items-start justify-between"
                        >
                            <div className="flex items-start space-x-3">
                                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                                <div>
                                    <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
                                    <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
                                </div>
                            </div>
                            <button
                                onClick={dismissError}
                                className="text-red-500 hover:text-red-700 dark:hover:text-red-300 p-1"
                                aria-label="Dismiss error"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    )}

                    {/* Scenario Selector */}
                    {!runbookContent && (
                        <ScenarioSelector onFilesLoaded={handleFilesLoaded} />
                    )}

                    {/* Results Section */}
                    {runbookContent && (
                        <section>
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Generated Runbook</h3>
                                <div className="flex space-x-2">
                                    <span className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded font-mono">Run ID: {runId}</span>
                                    <span className={`px-2 py-1 text-xs rounded font-bold uppercase ${jobStatus === 'SUCCESS' ? 'bg-green-100 text-green-800' :
                                        jobStatus === 'RUNNING' || jobStatus === 'PENDING' ? 'bg-blue-100 text-blue-800' :
                                            'bg-yellow-100 text-yellow-800'
                                        }`}>{jobStatus}</span>
                                </div>
                            </div>
                            <RunbookViewer content={runbookContent} metadata={runbookMetadata} />
                        </section>
                    )}

                    {/* Loading State */}
                    {(jobStatus === 'RUNNING' || jobStatus === 'PENDING') && !runbookContent && (
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 flex flex-col items-center justify-center">
                            <svg className="w-12 h-12 mb-4 animate-spin text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            <p className="text-gray-600 dark:text-gray-400">Processing pipeline...</p>
                        </div>
                    )}
                </div>

                {/* Status Bar */}
                <StatusBar
                    runId={runId}
                    status={jobStatus}
                    model={MODELS.find(m => m.id === selectedModel)?.name || selectedModel}
                    lastUpdated={lastUpdated}
                />
            </main>
        </div>
    );
}

export default App;
