/**
 * Accessibility Analysis Page
 */

'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function AccessibilityPage() {
  const [url, setUrl] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleRunAudit = async () => {
    if (!url) return;
    
    setLoading(true);
    try {
      const data = await apiClient.runAccessibilityAudit(url, ['wcag2a', 'wcag2aa']);
      setResults(data);
    } catch (error) {
      console.error('Accessibility audit failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-500';
      case 'serious':
        return 'bg-orange-100 border-orange-500';
      case 'moderate':
        return 'bg-yellow-100 border-yellow-500';
      default:
        return 'bg-blue-100 border-blue-500';
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Accessibility Audit (WCAG 2.1)</h1>

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
            {loading ? 'Auditing...' : 'Run Audit'}
          </button>
        </div>
      </div>

      {results && results.success && (
        <div>
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold">Accessibility Score</h2>
                <div className="text-sm text-gray-600">{results.compliance_level}</div>
              </div>
              <div className="text-5xl font-bold text-blue-600">
                {Math.round(results.score)}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center p-3 bg-red-50 rounded">
                <div className="text-2xl font-bold text-red-600">{results.summary.critical}</div>
                <div className="text-xs text-gray-600">Critical</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded">
                <div className="text-2xl font-bold text-orange-600">{results.summary.serious}</div>
                <div className="text-xs text-gray-600">Serious</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded">
                <div className="text-2xl font-bold text-yellow-600">{results.summary.moderate}</div>
                <div className="text-xs text-gray-600">Moderate</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded">
                <div className="text-2xl font-bold text-blue-600">{results.summary.minor}</div>
                <div className="text-xs text-gray-600">Minor</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded">
                <div className="text-2xl font-bold text-green-600">{results.summary.passes}</div>
                <div className="text-xs text-gray-600">Passed</div>
              </div>
            </div>
          </div>

          {['critical', 'serious', 'moderate'].map((severity) => {
            const violations = results.violations?.[severity] || [];
            if (violations.length === 0) return null;

            return (
              <div key={severity} className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-xl font-semibold mb-4 capitalize">{severity} Issues</h3>
                
                <div className="space-y-4">
                  {violations.map((violation: any, idx: number) => (
                    <div key={idx} className={`border-l-4 rounded p-4 ${getSeverityColor(severity)}`}>
                      <div className="font-medium mb-2">{violation.help}</div>
                      <div className="text-sm text-gray-700 mb-2">{violation.description}</div>
                      <div className="text-xs text-gray-600">
                        {violation.nodes_affected} element(s) affected
                      </div>
                      {violation.help_url && (
                        <a
                          href={violation.help_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Learn more →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
