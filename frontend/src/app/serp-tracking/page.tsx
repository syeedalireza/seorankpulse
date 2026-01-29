/**
 * SERP Tracking Page
 */

'use client';

import { useState } from 'react';
import { useKeywordTracking } from '@/hooks/useKeywordTracking';

export default function SERPTrackingPage() {
  const [projectId] = useState(1); // Would get from context/params
  const { keywords, checkRankings, addKeywords, isLoading } = useKeywordTracking(projectId);
  const [newKeywords, setNewKeywords] = useState('');
  const [location, setLocation] = useState('United States');

  const handleAddKeywords = async () => {
    const keywordList = newKeywords.split('\n').map(k => k.trim()).filter(Boolean);
    if (keywordList.length > 0) {
      await addKeywords.mutateAsync({ keywords: keywordList, location });
      setNewKeywords('');
    }
  };

  const handleCheckRankings = async () => {
    const keywordList = keywords.map((k: any) => k.keyword);
    await checkRankings.mutateAsync({ keywords: keywordList, location });
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">SERP Position Tracking</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Tracked Keywords</h2>
            
            {keywords.length === 0 ? (
              <p className="text-gray-500">No keywords tracked yet</p>
            ) : (
              <div className="space-y-2">
                {keywords.map((kw: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center p-3 border rounded">
                    <span className="font-medium">{kw.keyword}</span>
                    <span className="text-sm text-gray-600">Position: {kw.position || 'N/A'}</span>
                  </div>
                ))}
              </div>
            )}

            <button
              onClick={handleCheckRankings}
              className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              disabled={keywords.length === 0}
            >
              Check Rankings Now
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Add Keywords</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Location</label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full p-2 border rounded"
            >
              <option>United States</option>
              <option>United Kingdom</option>
              <option>Canada</option>
              <option>Australia</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Keywords (one per line)
            </label>
            <textarea
              value={newKeywords}
              onChange={(e) => setNewKeywords(e.target.value)}
              className="w-full p-2 border rounded h-32"
              placeholder="seo tools&#10;keyword research&#10;link building"
            />
          </div>

          <button
            onClick={handleAddKeywords}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Add Keywords
          </button>
        </div>
      </div>
    </div>
  );
}
