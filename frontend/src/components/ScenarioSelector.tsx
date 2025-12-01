import React, { useState } from 'react';
import { FileText, Database, ArrowRightLeft, Monitor, Upload } from 'lucide-react';
import { ScenarioCard } from './ScenarioCard';
import { api } from '../lib/api';

interface ScenarioSelectorProps {
    onFilesLoaded: (files: string[]) => void;
}

export function ScenarioSelector({ onFilesLoaded }: ScenarioSelectorProps) {
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [statusType, setStatusType] = useState<'info' | 'success' | 'error'>('info');

    const handleScenarioClick = async (scenario: string, scenarioName: string) => {
        setLoading(true);
        setStatus(`Loading ${scenarioName} data...`);
        setStatusType('info');

        try {
            const result = await api.loadDemoScenario(scenario);
            setStatus(`Successfully loaded ${result.files.length} files. Ready to generate.`);
            setStatusType('success');
            onFilesLoaded(result.files.map((f: any) => f.filename));
        } catch (error) {
            setStatus('Error loading demo data. Please try again.');
            setStatusType('error');
            console.error('Demo load error:', error);
        } finally {
            setLoading(false);
        }
    };

    const statusColors = {
        info: 'text-blue-600 dark:text-blue-400',
        success: 'text-green-600 dark:text-green-400',
        error: 'text-red-600 dark:text-red-400'
    };

    return (
        <section>
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                Import Source Data
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <ScenarioCard
                    icon={FileText}
                    iconColor="text-blue-600"
                    iconBgColor="bg-blue-50 dark:bg-blue-900/20"
                    label="Scenario A"
                    title="Kickoff Notes Only"
                    description="Import basic kickoff meeting notes to generate a preliminary scope."
                    hoverBorderColor="blue-400"
                    onClick={() => handleScenarioClick('kickoff', 'Kickoff Notes')}
                />

                <ScenarioCard
                    icon={Database}
                    iconColor="text-purple-600"
                    iconBgColor="bg-purple-50 dark:bg-purple-900/20"
                    label="Scenario B"
                    title="Full Engagement"
                    description="Import Slack exports, Jira tickets, and architecture docs for a complete runbook."
                    hoverBorderColor="purple-400"
                    onClick={() => handleScenarioClick('full', 'Full Engagement')}
                />

                <ScenarioCard
                    icon={ArrowRightLeft}
                    iconColor="text-orange-600"
                    iconBgColor="bg-orange-50 dark:bg-orange-900/20"
                    label="Scenario C"
                    title="Hadoop Migration"
                    description="Generate a migration plan from legacy Hadoop/Hive to Databricks Lakehouse."
                    hoverBorderColor="orange-400"
                    onClick={() => handleScenarioClick('migration', 'Hadoop Migration')}
                />

                <ScenarioCard
                    icon={Monitor}
                    iconColor="text-green-600"
                    iconBgColor="bg-green-50 dark:bg-green-900/20"
                    label="Scenario D"
                    title="MLOps Design"
                    description="Create an MLOps architecture runbook with MLflow and Model Serving."
                    hoverBorderColor="green-400"
                    onClick={() => handleScenarioClick('mlops', 'MLOps Design')}
                />

                {/* Upload Custom Files Card */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 flex flex-col items-center justify-center text-center cursor-pointer hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
                    <Upload className="w-8 h-8 text-gray-400 mb-2" />
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Upload Custom Files</span>
                    <input type="file" className="hidden" />
                </div>
            </div>

            {/* Status Message */}
            {status && (
                <div className={`mt-4 text-sm font-medium ${statusColors[statusType]} h-6`}>
                    {loading && <span className="inline-block animate-pulse">⏳ </span>}
                    {status}
                </div>
            )}
        </section>
    );
}
