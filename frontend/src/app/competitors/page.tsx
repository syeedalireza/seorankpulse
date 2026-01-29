/**
 * Competitive Analysis Page
 */

'use client';

import { useState } from 'react';
import { useCompetitors } from '@/hooks/useCompetitors';

export default function CompetitorsPage() {
  const [projectId] = useState(1);
  const { competitors, addCompetitor, compareCompetitors, contentGaps, fetchContentGaps } = useCompetitors(projectId);
  const [newCompetitor, setNewCompetitor] = useState('');
  const [comparisonResult, setComparisonResult] = useState<any>(null);

  const handleAddCompetitor = async () => {
    if (newCompetitor) {
      await addCompetitor.mutateAsync({ domain: newCompetitor });
      setNewCompetitor('');
    }
  };

  const handleCompare = async () => {
    const domains = competitors.map((c: any) => c.domain);
    const result = await compareCompetitors.mutateAsync(domains);
    setComparisonResult(result);
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Competitive Analysis</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Competitors</h2>
            
            {competitors.length === 0 ? (
              <p className="text-gray-500">No competitors added yet</p>
            ) : (
              <div className="space-y-3">
                {competitors.map((comp: any) => (
                  <div key={comp.id} className="flex justify-between items-center p-4 border rounded">
                    <div>
                      <div className="font-medium">{comp.domain}</div>
                      <div className="text-sm text-gray-600">{comp.name || comp.domain}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {competitors.length > 0 && (
              <button
                onClick={handleCompare}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Compare All
              </button>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Add Competitor</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Domain</label>
            <input
              type="text"
              value={newCompetitor}
              onChange={(e) => setNewCompetitor(e.target.value)}
              placeholder="competitor.com"
              className="w-full p-2 border rounded"
            />
          </div>

          <button
            onClick={handleAddCompetitor}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Add Competitor
          </button>
        </div>
      </div>

      {comparisonResult && (
        <div className="bg-white rounded-lg shadow p-6 mt-8">
          <h2 className="text-2xl font-semibold mb-6">Comparison Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-4 bg-green-50 rounded">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {comparisonResult.insights?.advantages?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Advantages</div>
            </div>
            
            <div className="text-center p-4 bg-red-50 rounded">
              <div className="text-3xl font-bold text-red-600 mb-2">
                {comparisonResult.insights?.disadvantages?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Disadvantages</div>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {comparisonResult.insights?.opportunities?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Opportunities</div>
            </div>
          </div>

          {comparisonResult.insights?.advantages && (
            <div className="mb-6">
              <h3 className="font-semibold text-green-700 mb-3">Your Advantages</h3>
              <ul className="space-y-2">
                {comparisonResult.insights.advantages.map((adv: string, idx: number) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span>{adv}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {comparisonResult.insights?.opportunities && (
            <div>
              <h3 className="font-semibold text-blue-700 mb-3">Opportunities</h3>
              <ul className="space-y-2">
                {comparisonResult.insights.opportunities.map((opp: string, idx: number) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-blue-500 mr-2">→</span>
                    <span>{opp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
