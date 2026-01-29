/**
 * Alerts & Monitoring Page
 */

'use client';

import { useState } from 'react';
import { useAlerts, useMonitoring } from '@/hooks/useAlerts';

export default function AlertsPage() {
  const [projectId] = useState(1);
  const { alerts, total, acknowledgeAlert } = useAlerts(projectId);
  const { startMonitoring, stopMonitoring } = useMonitoring(projectId);
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  const handleAcknowledge = async (alertId: number) => {
    await acknowledgeAlert.mutateAsync(alertId);
  };

  const handleStartMonitoring = async () => {
    await startMonitoring.mutateAsync({
      frequency: 'daily',
      thresholds: {
        seo_score_drop: 10,
        error_increase: 5,
      },
    });
  };

  const filteredAlerts = severityFilter === 'all'
    ? alerts
    : alerts.filter((a: any) => a.severity === severityFilter);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-900';
      case 'error':
        return 'bg-orange-100 border-orange-500 text-orange-900';
      case 'warning':
        return 'bg-yellow-100 border-yellow-500 text-yellow-900';
      default:
        return 'bg-blue-100 border-blue-500 text-blue-900';
    }
  };

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Alerts & Monitoring</h1>
        <div className="flex gap-4">
          <button
            onClick={handleStartMonitoring}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Start Monitoring
          </button>
        </div>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Filter by severity</label>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="all">All Alerts</option>
          <option value="critical">Critical</option>
          <option value="error">Error</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>

      <div className="space-y-4">
        {filteredAlerts.map((alert: any) => (
          <div
            key={alert.id}
            className={`border-l-4 rounded-lg p-6 ${getSeverityColor(alert.severity)}`}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-lg font-semibold">{alert.title}</h3>
              <span className="px-3 py-1 text-xs rounded bg-white">
                {alert.severity.toUpperCase()}
              </span>
            </div>
            
            <p className="text-sm mb-3">{alert.message}</p>
            
            <div className="flex justify-between items-center text-xs">
              <span>{new Date(alert.created_at).toLocaleString()}</span>
              {!alert.acknowledged && (
                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                >
                  Acknowledge
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredAlerts.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No alerts found</p>
        </div>
      )}
    </div>
  );
}
