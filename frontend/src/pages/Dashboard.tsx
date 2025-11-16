import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi } from '../lib/api';
import { Copy, Check } from 'lucide-react';
import type { Team } from '../types';

export function Dashboard() {
  const [copiedTeamId, setCopiedTeamId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'active' | 'archived'>('active');

  const { data: teams } = useQuery({
    queryKey: ['teams', activeTab],
    queryFn: async () => {
      const status = activeTab === 'active' ? 'active' : 'frozen';
      const response = await teamApi.getMyTeams(status);
      return response.data;
    },
  });

  const { data: myContributions } = useQuery({
    queryKey: ['my-contributions'],
    queryFn: async () => {
      const response = await contributionApi.getMyContributions();
      return response.data;
    },
  });

  const totalScore = myContributions?.reduce((sum, c) => sum + c.reputation_score, 0) || 0;

  const copyInviteCode = (teamId: number, inviteCode: string) => {
    navigator.clipboard.writeText(inviteCode);
    setCopiedTeamId(teamId);
    setTimeout(() => setCopiedTeamId(null), 2000);
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <Link
          to="/teams/new"
          className="px-4 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 text-sm"
        >
          Create Team
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Teams</p>
          <p className="text-2xl font-semibold text-gray-900">{teams?.length || 0}</p>
        </div>
        <div className="bg-white p-4 rounded border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Contributions</p>
          <p className="text-2xl font-semibold text-gray-900">{myContributions?.length || 0}</p>
        </div>
        <div className="bg-white p-4 rounded border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Total Score</p>
          <p className="text-2xl font-semibold text-gray-900">{totalScore.toFixed(1)}</p>
        </div>
      </div>

      {/* My Teams */}
      <div className="bg-white rounded border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Teams</h2>
            <div className="flex gap-1">
              <button
                onClick={() => setActiveTab('active')}
                className={`px-3 py-1 text-sm rounded ${
                  activeTab === 'active'
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setActiveTab('archived')}
                className={`px-3 py-1 text-sm rounded ${
                  activeTab === 'archived'
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Archived
              </button>
            </div>
          </div>
        </div>
        <div className="p-6">
          {!teams || teams.length === 0 ? (
            <div className="text-center py-12">
              {activeTab === 'active' ? (
                <>
                  <p className="text-gray-500 mb-4">No teams yet</p>
                  <div className="flex gap-3 justify-center">
                    <Link
                      to="/teams/new"
                      className="px-4 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 text-sm"
                    >
                      Create Team
                    </Link>
                    <Link
                      to="/teams/join"
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
                    >
                      Join Team
                    </Link>
                  </div>
                </>
              ) : (
                <p className="text-gray-500">No archived teams</p>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {teams.map((team) => (
                <div
                  key={team.id}
                  className="p-4 border border-gray-100 rounded hover:border-gray-300 transition"
                >
                  <Link to={`/teams/${team.id}`} className="block">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 mb-1">{team.name}</h3>
                        {team.description && (
                          <p className="text-sm text-gray-500 mb-2">{team.description}</p>
                        )}
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          <span>{team.member_count} members</span>
                          <span>•</span>
                          <span className="capitalize">{team.status}</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                  <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                    <code className="text-xs bg-gray-50 px-2 py-1 rounded text-gray-700 font-mono">
                      {team.invite_code}
                    </code>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        copyInviteCode(team.id, team.invite_code);
                      }}
                      className="text-xs text-gray-600 hover:text-gray-900 flex items-center gap-1"
                    >
                      {copiedTeamId === team.id ? (
                        <>
                          <Check className="h-3 w-3" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
