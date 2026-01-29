/**
 * Custom hook for competitive analysis
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useCompetitors(projectId: number) {
  const queryClient = useQueryClient();

  const competitorsQuery = useQuery({
    queryKey: ['competitors', projectId],
    queryFn: () => apiClient.getCompetitors(projectId),
    enabled: !!projectId,
  });

  const addCompetitor = useMutation({
    mutationFn: ({ domain, name }: { domain: string; name?: string }) =>
      apiClient.addCompetitor(projectId, domain, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors', projectId] });
    },
  });

  const compareCompetitors = useMutation({
    mutationFn: (competitorDomains: string[]) =>
      apiClient.compareCompetitors(projectId, competitorDomains),
  });

  const contentGapsQuery = useQuery({
    queryKey: ['content-gaps', projectId],
    queryFn: () => apiClient.getContentGaps(projectId),
    enabled: false, // Only fetch when explicitly requested
  });

  return {
    competitors: competitorsQuery.data?.competitors || [],
    isLoading: competitorsQuery.isLoading,
    error: competitorsQuery.error,
    addCompetitor,
    compareCompetitors,
    contentGaps: contentGapsQuery.data,
    fetchContentGaps: contentGapsQuery.refetch,
  };
}
