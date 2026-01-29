/**
 * Custom hook for alerts and monitoring
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useAlerts(projectId?: number, severity?: string) {
  const queryClient = useQueryClient();

  const alertsQuery = useQuery({
    queryKey: ['alerts', projectId, severity],
    queryFn: () => apiClient.getAlerts(projectId, severity),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const acknowledgeAlert = useMutation({
    mutationFn: (alertId: number) => apiClient.acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  return {
    alerts: alertsQuery.data?.alerts || [],
    total: alertsQuery.data?.total || 0,
    isLoading: alertsQuery.isLoading,
    error: alertsQuery.error,
    acknowledgeAlert,
  };
}

export function useMonitoring(projectId: number) {
  const queryClient = useQueryClient();

  const startMonitoring = useMutation({
    mutationFn: ({ frequency, thresholds }: { frequency: string; thresholds?: any }) =>
      apiClient.startMonitoring(projectId, frequency, thresholds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-status', projectId] });
    },
  });

  const stopMonitoring = useMutation({
    mutationFn: () => apiClient.stopMonitoring(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-status', projectId] });
    },
  });

  return {
    startMonitoring,
    stopMonitoring,
  };
}
