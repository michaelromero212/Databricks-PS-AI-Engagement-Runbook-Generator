export const MODELS = [
    { id: 'dbrx-instruct', name: 'Databricks DBRX Instruct', type: 'LLM', speed: 'Fast' },
    { id: 'distilbert-base-uncased', name: 'HuggingFace DistilBERT', type: 'NLP', speed: 'Very Fast' },
    { id: 'sentence-transformers/all-MiniLM-L6-v2', name: 'HuggingFace MiniLM', type: 'Embedding', speed: 'Instant' },
];

export const JOB_STATUS_COLORS = {
    PENDING: 'bg-yellow-500',
    RUNNING: 'bg-blue-500',
    SUCCESS: 'bg-green-500',
    FAILED: 'bg-red-500',
    TERMINATED: 'bg-gray-500',
    SKIPPED: 'bg-gray-400',
    INTERNAL_ERROR: 'bg-red-700',
};
