'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { UploadCloud, FileSpreadsheet, FileText, AlertCircle, CheckCircle2, Loader2, Building } from 'lucide-react';

interface FileUploaderProps {
  onSuccess?: (uploadId: number) => void;
}

export default function FileUploader({ onSuccess }: FileUploaderProps) {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [companyName, setCompanyName] = useState('Acme Corporation');
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const [processingStage, setProcessingStage] = useState<string>('Preparing upload...');

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    if (selectedFile.size > 250 * 1024 * 1024) {
      setError('File size exceeds maximum allowed 250MB limit.');
      return;
    }
    setFile(selectedFile);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a financial document (PDF, Excel, Word, CSV, TXT, JSON) first.');
      return;
    }

    setIsUploading(true);
    setProgress(5);
    setProcessingStage('Uploading document to secure server...');
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_name', companyName || '');

    try {
      const res = await api.post('/api/upload/', formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 60) / progressEvent.total);
            setProgress(Math.max(5, percentCompleted));
            if (percentCompleted < 60) {
              setProcessingStage(`Uploading document (${(progressEvent.loaded / (1024 * 1024)).toFixed(1)} MB / ${(progressEvent.total / (1024 * 1024)).toFixed(1)} MB)...`);
            } else {
              setProcessingStage('Parsing workbook & extracting financial schedules...');
            }
          }
        }
      });

      setProgress(100);
      setProcessingStage('Finalizing statements & financial intelligence...');

      const uploadId = res.data.upload_id;
      if (onSuccess) onSuccess(uploadId);
      router.push(`/analysis/${uploadId}`);
    } catch (err: any) {
      setIsUploading(false);
      setProgress(0);
      setProcessingStage('');
      console.error("Upload API Error Response:", err.response?.data);
      const serverMsg = err.response?.data?.detail;
      setError(typeof serverMsg === 'string' ? serverMsg : 'Failed to process financial workbook. Ensure file format is valid.');
    }
  };

  const isSpreadsheet = file && /\.(xlsx|xls|csv)$/i.test(file.name);

  return (
    <div className="glass-card rounded-2xl p-6 shadow-sm border border-slate-200">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold">
          <UploadCloud className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">Upload Financial Document</h3>
          <p className="text-xs text-slate-500">AI extracts multi-MB sheets, PDF tables, Dr/Cr ledgers, statements, & ratios fast</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
            <Building className="w-3.5 h-3.5 text-slate-400" />
            Company / Entity Name
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g. Acme Global Inc."
            required
            className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
          />
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleFileDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
            isDragOver
              ? 'border-brand-500 bg-brand-50/50'
              : file
              ? 'border-emerald-300 bg-emerald-50/30'
              : 'border-slate-200 bg-slate-50/50 hover:bg-slate-50'
          }`}
        >
          <input
            type="file"
            id="file-upload"
            accept=".pdf,.xlsx,.xls,.csv,.doc,.docx,.txt,.json,.xml,.pptx,.ppt,.png,.jpg,.jpeg,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,application/json,image/*"
            onChange={handleFileChange}
            className="hidden"
          />

          {!file ? (
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <div className="w-12 h-12 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center text-brand-600 mb-3 animate-pulse">
                <FileText className="w-6 h-6" />
              </div>
              <p className="text-sm font-semibold text-slate-800">
                Drag and drop your Financial Document here, or <span className="text-brand-600 underline">browse</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">Supports PDF, Excel, Word, CSV, TXT, JSON, Images up to <span className="font-semibold text-brand-600">250MB</span></p>
              <p className="text-[11px] text-slate-400 mt-2 italic">Optimized for high-speed multi-sheet extraction, Trial Balance, P&L, Balance Sheet & Reports</p>
            </label>
          ) : (
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-white p-3.5 rounded-xl border border-emerald-200 shadow-sm gap-3">
              <div className="flex items-center gap-3 text-left min-w-0 w-full sm:w-auto">
                {isSpreadsheet ? (
                  <FileSpreadsheet className="w-8 h-8 text-emerald-600 shrink-0" />
                ) : (
                  <FileText className="w-8 h-8 text-emerald-600 shrink-0" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-bold text-slate-900 truncate">{file.name}</p>
                  <p className="text-xs text-slate-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="text-xs font-semibold text-rose-600 hover:bg-rose-50 px-2.5 py-1 rounded-lg shrink-0 self-end sm:self-auto"
              >
                Change File
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2.5 text-xs text-rose-700 font-medium">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {isUploading && (
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-semibold text-slate-600">
              <span className="flex items-center gap-1.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-brand-600" />
                {processingStage}
              </span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-500 to-cyan-500 transition-all duration-300 rounded-full"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        <div className="pt-1">
          <button
            type="submit"
            disabled={!file || isUploading}
            className="w-full py-3 bg-gradient-to-r from-brand-700 to-brand-600 hover:from-brand-800 hover:to-brand-700 text-white font-bold text-sm rounded-xl shadow-md shadow-brand-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing Large Financial Document...</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Run Fast AI Financial Analysis</span>
              </>
            )}
          </button>

          <div className="pt-2 text-center">
            <button
              type="button"
              disabled={isUploading}
              onClick={async () => {
                setIsUploading(true);
                setProgress(30);
                try {
                  const res = await api.post('/api/upload/sample');
                  setProgress(100);
                  setTimeout(() => {
                    const uploadId = res.data.upload_id;
                    if (onSuccess) onSuccess(uploadId);
                    router.push(`/analysis/${uploadId}`);
                  }, 500);
                } catch (err: any) {
                  setIsUploading(false);
                  setError(err.response?.data?.detail || 'Failed to process sample workbook.');
                }
              }}
              className="text-xs font-bold text-brand-600 hover:text-brand-800 hover:underline flex items-center justify-center gap-1 mx-auto"
            >
              <span>⚡ Don't have a file? Run instant demo analysis with sample workbook</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
