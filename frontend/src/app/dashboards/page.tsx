/**
 * Custom Dashboards Page
 */

'use client';

import { useState } from 'react';
import { useDashboards, useWidgetTypes } from '@/hooks/useDashboards';

export default function DashboardsPage() {
  const { dashboards, isLoading, createDashboard } = useDashboards();
  const { data: widgetTypes } = useWidgetTypes();
  const [selectedDashboard, setSelectedDashboard] = useState<number | null>(null);

  const handleCreateDashboard = async () => {
    await createDashboard.mutateAsync({
      name: 'New Dashboard',
      description: 'Custom SEO dashboard',
      layout: {},
      widgets: [],
    });
  };

  if (isLoading) {
    return <div className="p-8">Loading dashboards...</div>;
  }

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Custom Dashboards</h1>
        <button
          onClick={handleCreateDashboard}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Create Dashboard
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboards.map((dashboard: any) => (
          <div
            key={dashboard.id}
            className="border rounded-lg p-6 hover:shadow-lg cursor-pointer transition-shadow"
            onClick={() => setSelectedDashboard(dashboard.id)}
          >
            <h3 className="text-xl font-semibold mb-2">{dashboard.name}</h3>
            {dashboard.description && (
              <p className="text-gray-600 mb-4">{dashboard.description}</p>
            )}
            <div className="text-sm text-gray-500">
              {dashboard.widgets?.length || 0} widgets
            </div>
          </div>
        ))}
      </div>

      {dashboards.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No dashboards yet</p>
          <button
            onClick={handleCreateDashboard}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create Your First Dashboard
          </button>
        </div>
      )}

      {selectedDashboard && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Dashboard Editor</h2>
          <p className="text-gray-600">
            Dashboard builder UI would go here with drag-and-drop functionality
          </p>
        </div>
      )}
    </div>
  );
}
