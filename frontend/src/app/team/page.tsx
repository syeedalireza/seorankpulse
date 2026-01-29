/**
 * Team Collaboration Page
 */

'use client';

import { useState } from 'react';
import { useTeam } from '@/hooks/useTeam';

export default function TeamPage() {
  const [projectId] = useState(1); // Would get from context/params
  const { team, tasks, comments, inviteMember, createTask, addComment } = useTeam(projectId);
  const [activeTab, setActiveTab] = useState<'members' | 'tasks' | 'comments'>('members');

  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('viewer');

  const handleInvite = async () => {
    if (inviteEmail) {
      await inviteMember.mutateAsync({ email: inviteEmail, role: inviteRole });
      setInviteEmail('');
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Team Collaboration</h1>

      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            {['members', 'tasks', 'comments'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {activeTab === 'members' && (
        <div>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Team Members</h2>
            
            <div className="space-y-3">
              {team.map((member: any) => (
                <div key={member.id} className="flex justify-between items-center p-3 border rounded">
                  <div>
                    <div className="font-medium">User ID: {member.user_id}</div>
                    <div className="text-sm text-gray-600">Role: {member.role}</div>
                  </div>
                  <span className="px-3 py-1 bg-gray-100 rounded text-sm">
                    {member.role}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Invite Team Member</h3>
            
            <div className="flex gap-4">
              <input
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="email@example.com"
                className="flex-1 p-2 border rounded"
              />
              
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
                className="p-2 border rounded"
              >
                <option value="viewer">Viewer</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>

              <button
                onClick={handleInvite}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Invite
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'tasks' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Tasks</h2>
          
          <div className="space-y-3">
            {tasks.map((task: any) => (
              <div key={task.id} className="p-4 border rounded">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold">{task.title}</h3>
                  <span className={`px-2 py-1 text-xs rounded ${
                    task.priority === 'critical' ? 'bg-red-100 text-red-800' :
                    task.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {task.priority}
                  </span>
                </div>
                {task.description && (
                  <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                )}
                <div className="text-xs text-gray-500">Status: {task.status}</div>
              </div>
            ))}
          </div>

          {tasks.length === 0 && (
            <p className="text-gray-500 text-center py-8">No tasks yet</p>
          )}
        </div>
      )}

      {activeTab === 'comments' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Comments</h2>
          
          <div className="space-y-4">
            {comments.map((comment: any) => (
              <div key={comment.id} className="border-l-4 border-blue-500 pl-4 py-2">
                <p className="text-sm">{comment.content}</p>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(comment.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>

          {comments.length === 0 && (
            <p className="text-gray-500 text-center py-8">No comments yet</p>
          )}
        </div>
      )}
    </div>
  );
}
