/**
 * Duplicate Content Detection Page
 */

'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function DuplicatesPage() {
  const [projectId] = useState(1);
  const [threshold, setThreshold] = useState(3);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleDetect = async () => {
    setLoading(true);
    try {
      const data = await apiClient.detectDuplicates(projectId, threshold);
      setResults(data);
    } catch (error) {
      console.error('Duplicate detection failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Duplicate Content Detection</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">Similarity Threshold</label>
            <input
              type="range"
              min="1"
              max="10"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 mt-1">
              Current: {threshold} (lower = more strict)
            </div>
          </div>
          
          <button
            onClick={handleDetect}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Detecting...' : 'Detect Duplicates'}
          </button>
        </div>
      </div>

      {results && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {results.total_pages_analyzed}
              </div>
              <div className="text-sm text-gray-600">Pages Analyzed</div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {results.exact_duplicate_groups}
              </div>
              <div className="text-sm text-gray-600">Exact Duplicates</div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">
                {results.near_duplicate_groups}
              </div>
              <div className="text-sm text-gray-600">Near Duplicates</div>
            </div>
          </div>

          {results.exact_duplicates && results.exact_duplicates.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Exact Duplicates</h2>
              
              <div className="space-y-4">
                {results.exact_duplicates.map((group: any, idx: number) => (
                  <div key={idx} className="border rounded-lg p-4">
                    <div className="font-medium mb-2">
                      Group {idx + 1} ({group.count} pages)
                    </div>
                    <ul className="space-y-1">
                      {group.urls.map((url: string, urlIdx: number) => (
                        <li key={urlIdx} className="text-sm text-blue-600 hover:underline">
                          <a href={url} target="_blank" rel="noopener noreferrer">
                            {url}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.near_duplicates && results.near_duplicates.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Near Duplicates</h2>
              
              <div className="space-y-4">
                {results.near_duplicates.map((group: any, idx: number) => (
                  <div key={idx} className="border rounded-lg p-4">
                    <div className="font-medium mb-2">
                      Group {idx + 1} ({group.count} similar pages)
                    </div>
                    <ul className="space-y-1">
                      {group.urls.map((url: string, urlIdx: number) => (
                        <li key={urlIdx} className="text-sm text-blue-600 hover:underline">
                          <a href={url} target="_blank" rel="noopener noreferrer">
                            {url}
                          </a>
                        </li>
                      ))}
                    </ul>
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
