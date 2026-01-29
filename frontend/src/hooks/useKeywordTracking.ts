/**
 * Custom hook for SERP keyword tracking
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useKeywordTracking(projectId: number) {
  const queryClient = useQueryClient();

  const keywordsQuery = useQuery({
    queryKey: ['keywords', projectId],
    queryFn: () => apiClient.getKeywords(projectId),
    enabled: !!projectId,
  });

  const addKeywords = useMutation({
    mutationFn: ({ keywords, location }: { keywords: string[]; location: string }) =>
      apiClient.addKeywords(projectId, keywords, location),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords', projectId] });
    },
  });

  const checkRankings = useMutation({
    mutationFn: ({ keywords, location }: { keywords: string[]; location: string }) =>
      apiClient.checkRankings(projectId, keywords, location),
  });

  return {
    keywords: keywordsQuery.data?.keywords || [],
    isLoading: keywordsQuery.isLoading,
    error: keywordsQuery.error,
    addKeywords,
    checkRankings,
  };
}
