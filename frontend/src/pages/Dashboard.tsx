import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi } from '../lib/api';
import { Users, FileText, TrendingUp, Plus, Copy, Check } from 'lucide-react';
import type { Team, Contribution } from '../types';

export function Dashboard() {
  const [copiedTeamId, setCopiedTeamId] = useState<number | null>(null);

  const { data: teams } = useQuery({
    queryKey: ['teams'],
    queryFn: async () => {
      const response = await teamApi.getMyTeams();
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
  const totalVerifications = myContributions?.reduce((sum, c) => sum + c.verification_count, 0) || 0;

  const copyInviteCode = (teamId: number, inviteCode: string) => {
    navigator.clipboard.writeText(inviteCode);
    setCopiedTeamId(teamId);
    setTimeout(() => setCopiedTeamId(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <Link
          to="/teams/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Create Team
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-600">Teams</p>
              <p className="text-2xl font-bold text-gray-900">{teams?.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-600">Contributions</p>
              <p className="text-2xl font-bold text-gray-900">{myContributions?.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total Score</p>
              <p className="text-2xl font-bold text-gray-900">{totalScore.toFixed(1)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* My Teams */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">My Teams</h2>
        </div>
        <div className="p-6">
          {!teams || teams.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No teams yet. Create or join one to get started!</p>
              <div className="mt-4 space-x-4">
                <Link
                  to="/teams/new"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Create Team
                </Link>
                <Link
                  to="/teams/join"
                  className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                >
                  Join Team
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {teams.map((team) => (
                <div
                  key={team.id}
                  className="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                >
                  <Link to={`/teams/${team.id}`}>
                    <h3 className="font-semibold text-gray-900">{team.name}</h3>
                    {team.description && (
                      <p className="text-sm text-gray-600 mt-1">{team.description}</p>
                    )}
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <Users className="h-4 w-4 mr-1" />
                      {team.member_count} members
                      <span className="mx-2">•</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        team.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {team.status}
                      </span>
                    </div>
                  </Link>
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 mr-2">
                        <p className="text-xs text-gray-500 mb-1">Invite Code</p>
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-900 font-mono">
                          {team.invite_code}
                        </code>
                      </div>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          copyInviteCode(team.id, team.invite_code);
                        }}
                        className="px-3 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100 flex items-center"
                        title="Copy invite code"
                      >
                        {copiedTeamId === team.id ? (
                          <>
                            <Check className="h-3 w-3 mr-1" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3 mr-1" />
                            Copy
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Contributions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">My Recent Contributions</h2>
        </div>
        <div className="p-6">
          {!myContributions || myContributions.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No contributions yet. Start contributing to your teams!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {myContributions.slice(0, 5).map((contribution) => (
                <div
                  key={contribution.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900">{contribution.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {new Date(contribution.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        Score: {contribution.reputation_score.toFixed(1)}
                      </p>
                      <p className="text-xs text-gray-600">
                        {contribution.verification_count} verifications
                      </p>
                    </div>
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
