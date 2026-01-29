/**
 * Custom hook for team collaboration
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useTeam(projectId: number) {
  const queryClient = useQueryClient();

  const teamQuery = useQuery({
    queryKey: ['team', projectId],
    queryFn: () => apiClient.getTeamMembers(projectId),
    enabled: !!projectId,
  });

  const inviteMember = useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) =>
      apiClient.inviteTeamMember(projectId, email, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team', projectId] });
    },
  });

  const commentsQuery = useQuery({
    queryKey: ['comments', projectId],
    queryFn: () => apiClient.getComments(projectId),
    enabled: !!projectId,
  });

  const addComment = useMutation({
    mutationFn: ({ content, pageId }: { content: string; pageId?: number }) =>
      apiClient.createComment(projectId, content, pageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', projectId] });
    },
  });

  const tasksQuery = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => apiClient.getTasks(projectId),
    enabled: !!projectId,
  });

  const createTask = useMutation({
    mutationFn: (task: any) => apiClient.createTask(projectId, task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
  });

  const updateTask = useMutation({
    mutationFn: ({ taskId, updates }: { taskId: number; updates: any }) =>
      apiClient.updateTask(taskId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
  });

  return {
    team: teamQuery.data || [],
    comments: commentsQuery.data || [],
    tasks: tasksQuery.data || [],
    isLoading: teamQuery.isLoading || commentsQuery.isLoading || tasksQuery.isLoading,
    inviteMember,
    addComment,
    createTask,
    updateTask,
  };
}
