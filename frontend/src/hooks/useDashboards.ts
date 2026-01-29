/**
 * Custom hook for dashboard management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useDashboards(projectId?: number) {
  const queryClient = useQueryClient();

  const dashboardsQuery = useQuery({
    queryKey: ['dashboards', projectId],
    queryFn: () => apiClient.getDashboards(projectId),
  });

  const createDashboard = useMutation({
    mutationFn: (data: any) => apiClient.createDashboard(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
    },
  });

  const updateDashboard = useMutation({
    mutationFn: ({ id, updates }: { id: number; updates: any }) =>
      apiClient.updateDashboard(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
    },
  });

  const addWidget = useMutation({
    mutationFn: ({ dashboardId, widget }: { dashboardId: number; widget: any }) =>
      apiClient.addWidget(dashboardId, widget),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
    },
  });

  return {
    dashboards: dashboardsQuery.data?.dashboards || [],
    isLoading: dashboardsQuery.isLoading,
    error: dashboardsQuery.error,
    createDashboard,
    updateDashboard,
    addWidget,
  };
}

export function useWidgetTypes() {
  return useQuery({
    queryKey: ['widget-types'],
    queryFn: () => apiClient.getWidgetTypes(),
  });
}
