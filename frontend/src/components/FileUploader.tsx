import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle } from 'lucide-react';
import { api } from '../lib/api';

interface FileUploaderProps {
    onUploadComplete: (filename: string) => void;
}

export function FileUploader({ onUploadComplete }: FileUploaderProps) {
    const [files, setFiles] = useState<File[]>([]);
    const [uploading, setUploading] = useState(false);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        setFiles(prev => [...prev, ...acceptedFiles]);
        // Auto upload for prototype
        acceptedFiles.forEach(async (file) => {
            setUploading(true);
            try {
                await api.uploadFile(file);
                onUploadComplete(file.name);
            } catch (e) {
                console.error(e);
            } finally {
                setUploading(false);
            }
        });
    }, [onUploadComplete]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

    return (
        <div className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 dark:bg-gray-900 dark:border-gray-700">
            <div {...getRootProps()} className="cursor-pointer flex flex-col items-center justify-center p-6">
                <input {...getInputProps()} />
                <Upload className="h-10 w-10 text-gray-400 mb-2" />
                {isDragActive ? (
                    <p className="text-sm text-gray-500">Drop the files here ...</p>
                ) : (
                    <p className="text-sm text-gray-500">Drag & drop files here, or click to select files</p>
                )}
            </div>

            {files.length > 0 && (
                <div className="mt-4 space-y-2">
                    {files.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded shadow-sm">
                            <div className="flex items-center space-x-2">
                                <File className="h-4 w-4 text-primary" />
                                <span className="text-sm truncate max-w-[200px]">{file.name}</span>
                            </div>
                            {uploading ? (
                                <span className="text-xs text-yellow-500">Uploading...</span>
                            ) : (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
