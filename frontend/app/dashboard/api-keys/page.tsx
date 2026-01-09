'use client';

import { useState, useEffect } from 'react';
import { authAPI } from '@/lib/api-client';
import { useAuthStore } from '@/lib/store';
import { Key, Copy, RefreshCw, Eye, EyeOff, CheckCircle, Shield, Code, Terminal } from 'lucide-react';

export default function APIKeysPage() {
  const user = useAuthStore((state) => state.user);
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Load API key from localStorage or user object
    const storedKey = localStorage.getItem('api_key') || user?.api_key || '';
    setApiKey(storedKey);
  }, [user]);

  const handleRegenerate = async () => {
    if (!confirm('Are you sure you want to regenerate your API key? The old key will stop working immediately.')) {
      return;
    }

    setRegenerating(true);
    try {
      const response = await authAPI.regenerateApiKey();
      setApiKey(response.api_key);
      localStorage.setItem('api_key', response.api_key);
      alert('API key regenerated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to regenerate API key');
    } finally {
      setRegenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const maskedKey = apiKey ? `${apiKey.substring(0, 8)}${'•'.repeat(24)}` : '';

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-slate-900 mb-2">API Keys</h1>
        <p className="text-slate-600">Manage your API credentials for programmatic access</p>
      </div>

      {/* API Key Card */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
        <div className="flex items-center mb-6">
          <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center mr-3">
            <Key className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h2 className="text-xl font-serif font-bold text-slate-900">Your API Key</h2>
            <p className="text-sm text-slate-500">Use this key to authenticate API requests</p>
          </div>
        </div>

        <div className="bg-slate-900 rounded-xl p-5 mb-4">
          <div className="flex items-center justify-between">
            <code className="text-sm font-mono text-amber-400 flex-1">
              {showKey ? apiKey : maskedKey}
            </code>
            <div className="flex items-center space-x-2 ml-4">
              <button
                onClick={() => setShowKey(!showKey)}
                className="p-2 text-slate-400 hover:text-white transition rounded-lg hover:bg-slate-800"
                title={showKey ? 'Hide' : 'Show'}
              >
                {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
              <button
                onClick={handleCopy}
                className="p-2 text-slate-400 hover:text-white transition rounded-lg hover:bg-slate-800"
                title="Copy"
              >
                {copied ? (
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                ) : (
                  <Copy className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          className="flex items-center px-5 py-2.5 bg-slate-100 text-red-600 border border-slate-200 rounded-lg hover:bg-red-50 hover:border-red-200 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${regenerating ? 'animate-spin' : ''}`} />
          {regenerating ? 'Regenerating...' : 'Regenerate API Key'}
        </button>

        <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start">
          <Shield className="w-5 h-5 text-amber-600 mr-3 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-amber-900">
            <strong>Security Notice:</strong> Regenerating your API key will immediately invalidate the old key.
            Update all applications using the old key before regenerating.
          </p>
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center mb-6">
          <Code className="w-5 h-5 text-amber-600 mr-2" />
          <h2 className="text-xl font-serif font-bold text-slate-900">API Documentation</h2>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
              <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full text-xs flex items-center justify-center mr-2 font-bold">1</span>
              Authentication Header
            </h3>
            <p className="text-slate-600 mb-3 ml-8">
              Include your API key in the request header:
            </p>
            <div className="bg-slate-900 rounded-xl p-4 overflow-x-auto ml-8">
              <code className="text-sm text-amber-400">
                X-API-Key: {apiKey || 'your_api_key_here'}
              </code>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
              <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full text-xs flex items-center justify-center mr-2 font-bold">2</span>
              cURL Example
            </h3>
            <div className="bg-slate-900 rounded-xl p-4 overflow-x-auto ml-8">
              <pre className="text-sm text-emerald-400">
{`curl -X POST http://localhost:8000/api/v1/analyze \\
  -H "X-API-Key: ${apiKey || 'your_api_key_here'}" \\
  -F "file=@contract.pdf"`}
              </pre>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
              <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full text-xs flex items-center justify-center mr-2 font-bold">3</span>
              Python Example
            </h3>
            <div className="bg-slate-900 rounded-xl p-4 overflow-x-auto ml-8">
              <pre className="text-sm text-emerald-400">
{`import requests

url = "http://localhost:8000/api/v1/analyze"
headers = {"X-API-Key": "${apiKey || 'your_api_key_here'}"}
files = {"file": open("contract.pdf", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())`}
              </pre>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-slate-900 mb-2 flex items-center">
              <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full text-xs flex items-center justify-center mr-2 font-bold">4</span>
              JavaScript Example
            </h3>
            <div className="bg-slate-900 rounded-xl p-4 overflow-x-auto ml-8">
              <pre className="text-sm text-emerald-400">
{`const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'X-API-Key': '${apiKey || 'your_api_key_here'}'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));`}
              </pre>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-start">
          <Terminal className="w-5 h-5 text-slate-600 mr-3 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-slate-700">
            <strong>Pro Tip:</strong> Store your API key in environment variables rather than hardcoding it in your application.
            Never commit API keys to version control.
          </p>
        </div>
      </div>
    </div>
  );
}

