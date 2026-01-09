'use client';

import { useState } from 'react';
import { contractAPI } from '@/lib/api-client';
import { ContractAnalysisResult } from '@/lib/types';
import { Upload, FileText, AlertCircle, CheckCircle, Loader, Scale, Gavel, Shield } from 'lucide-react';

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<ContractAnalysisResult | null>(null);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF or Word document');
        return;
      }

      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
      setError('');
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError('');

    try {
      const data = await contractAPI.analyze(file);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze contract. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'medium':
        return 'text-amber-700 bg-amber-50 border-amber-200';
      case 'low':
        return 'text-emerald-700 bg-emerald-50 border-emerald-200';
      default:
        return 'text-slate-600 bg-slate-50 border-slate-200';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'low':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-slate-900 mb-2">Analyze Contract</h1>
        <p className="text-slate-600">Upload a legal document for AI-powered analysis and risk assessment</p>
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-8">
        <div className="border-2 border-dashed border-slate-300 rounded-xl p-12 text-center hover:border-amber-400 hover:bg-amber-50/30 transition-all cursor-pointer group">
          <div className="w-20 h-20 bg-gradient-to-br from-amber-500/10 to-amber-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-105 transition-transform">
            <Upload className="w-10 h-10 text-amber-600" />
          </div>

          <label htmlFor="file-upload" className="cursor-pointer">
            <span className="text-xl font-serif font-semibold text-slate-900 block mb-2">
              {file ? file.name : 'Choose a file or drag it here'}
            </span>
            <p className="text-sm text-slate-500">
              PDF or Word documents up to 10MB
            </p>
            <input
              id="file-upload"
              type="file"
              className="hidden"
              accept=".pdf,.doc,.docx"
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="mt-6">
              <div className="inline-flex items-center px-5 py-3 bg-amber-50 border border-amber-200 rounded-xl">
                <FileText className="w-5 h-5 text-amber-600 mr-3" />
                <span className="text-sm font-medium text-amber-900">{file.name}</span>
                <CheckCircle className="w-4 h-4 text-emerald-500 ml-3" />
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={!file || analyzing}
          className="mt-6 w-full bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 py-4 px-6 rounded-xl font-semibold hover:from-amber-400 hover:to-amber-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg shadow-amber-500/20"
        >
          {analyzing ? (
            <>
              <Loader className="w-5 h-5 mr-2 animate-spin" />
              Analyzing Document...
            </>
          ) : (
            <>
              <Gavel className="w-5 h-5 mr-2" />
              Analyze Contract
            </>
          )}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Analysis Complete Banner */}
          <div className="bg-gradient-to-r from-emerald-50 to-emerald-100/50 border border-emerald-200 rounded-xl p-5 flex items-center">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mr-4">
              <CheckCircle className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <p className="text-emerald-900 font-semibold">Analysis Complete</p>
              <p className="text-sm text-emerald-700">Your contract has been reviewed by our AI legal assistant</p>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center mb-4">
              <Scale className="w-5 h-5 text-amber-600 mr-2" />
              <h2 className="text-xl font-serif font-bold text-slate-900">Executive Summary</h2>
            </div>
            <p className="text-slate-700 leading-relaxed">{result.analysis.summary}</p>
          </div>

          {/* Parties */}
          {result.analysis.parties.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-serif font-bold text-slate-900 mb-4">Contracting Parties</h2>
              <div className="space-y-3">
                {result.analysis.parties.map((party, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                    <span className="font-medium text-slate-900">{party.name}</span>
                    <span className="text-sm text-slate-600 capitalize px-3 py-1 bg-slate-200/50 rounded-full">{party.role}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Terms */}
          {result.analysis.key_terms.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-xl font-serif font-bold text-slate-900 mb-4">Key Terms & Clauses</h2>
              <div className="space-y-4">
                {result.analysis.key_terms.map((term, idx) => (
                  <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                    <h3 className="font-semibold text-slate-900 mb-2">{term.term}</h3>
                    <p className="text-sm text-slate-600 leading-relaxed">{term.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risks */}
          {result.analysis.risks.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center mb-4">
                <Shield className="w-5 h-5 text-red-600 mr-2" />
                <h2 className="text-xl font-serif font-bold text-slate-900">Risk Assessment</h2>
              </div>
              <div className="space-y-4">
                {result.analysis.risks.map((risk, idx) => (
                  <div key={idx} className={`p-5 border rounded-xl ${getSeverityColor(risk.severity)}`}>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold capitalize text-lg">{risk.category}</h3>
                      <span className={`text-xs font-bold uppercase px-3 py-1.5 rounded-full border ${getSeverityBadge(risk.severity)}`}>
                        {risk.severity} Risk
                      </span>
                    </div>
                    <p className="text-sm mb-3 leading-relaxed">{risk.description}</p>
                    {risk.recommendation && (
                      <div className="pt-3 border-t border-current/10">
                        <p className="text-sm">
                          <span className="font-semibold">Recommendation:</span> {risk.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-xl font-serif font-bold text-slate-900 mb-4">Document Information</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 uppercase tracking-wide mb-1">Pages</p>
                <p className="text-2xl font-serif font-bold text-slate-900">{result.metadata.pages}</p>
              </div>
              <div className="text-center p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 uppercase tracking-wide mb-1">Word Count</p>
                <p className="text-2xl font-serif font-bold text-slate-900">{result.metadata.word_count.toLocaleString()}</p>
              </div>
              <div className="text-center p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 uppercase tracking-wide mb-1">Processing Time</p>
                <p className="text-2xl font-serif font-bold text-slate-900">
                  {result.metadata.processing_time.toFixed(2)}s
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

