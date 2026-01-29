/**
 * Lighthouse Core Web Vitals Analysis Page
 */

'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function LighthousePage() {
  const [url, setUrl] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleRunAudit = async () => {
    if (!url) return;
    
    setLoading(true);
    try {
      const data = await apiClient.runLighthouseAudit(url);
      setResults(data);
    } catch (error) {
      console.error('Lighthouse audit failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Lighthouse Core Web Vitals</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex gap-4">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="flex-1 p-3 border rounded"
          />
          <button
            onClick={handleRunAudit}
            disabled={loading || !url}
            className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Running...' : 'Run Audit'}
          </button>
        </div>
      </div>

      {results && results.success && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {Object.entries(results.scores || {}).map(([key, value]: [string, any]) => (
              <div key={key} className="bg-white rounded-lg shadow p-6 text-center">
                <div className={`text-4xl font-bold mb-2 ${getScoreColor(value)}`}>
                  {Math.round(value)}
                </div>
                <div className="text-sm text-gray-600 uppercase">{key.replace('_', ' ')}</div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-2xl font-semibold mb-6">Core Web Vitals</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">Largest Contentful Paint (LCP)</div>
                <div className="text-3xl font-bold mb-1">{results.core_web_vitals?.lcp?.toFixed(2)}s</div>
                <div className={`text-sm ${getScoreColor(results.core_web_vitals?.lcp_score || 0)}`}>
                  Score: {Math.round(results.core_web_vitals?.lcp_score || 0)}
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">Cumulative Layout Shift (CLS)</div>
                <div className="text-3xl font-bold mb-1">{results.core_web_vitals?.cls?.toFixed(3)}</div>
                <div className={`text-sm ${getScoreColor(results.core_web_vitals?.cls_score || 0)}`}>
                  Score: {Math.round(results.core_web_vitals?.cls_score || 0)}
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="text-sm text-gray-600 mb-2">First Input Delay (FID)</div>
                <div className="text-3xl font-bold mb-1">{Math.round(results.core_web_vitals?.fid_estimate || 0)}ms</div>
                <div className={`text-sm ${getScoreColor(results.core_web_vitals?.fid_score || 0)}`}>
                  Score: {Math.round(results.core_web_vitals?.fid_score || 0)}
                </div>
              </div>
            </div>
          </div>

          {results.opportunities && results.opportunities.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-semibold mb-4">Optimization Opportunities</h2>
              
              <div className="space-y-3">
                {results.opportunities.map((opp: any, idx: number) => (
                  <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="font-medium">{opp.title}</div>
                    <div className="text-sm text-gray-600">{opp.description}</div>
                    {opp.savings_ms > 0 && (
                      <div className="text-xs text-gray-500 mt-1">
                        Potential savings: {Math.round(opp.savings_ms)}ms
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
