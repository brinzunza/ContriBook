import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi, verificationApi } from '../lib/api';
import { Plus, Check, Copy, Search } from 'lucide-react';
import type { Contribution } from '../types';
import { useAuth } from '../contexts/AuthContext';

export function TeamDetail() {
  const { teamId } = useParams<{ teamId: string }>();
  const { user } = useAuth();
  const [copiedInvite, setCopiedInvite] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterContributor, setFilterContributor] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<string>('desc');

  const { data: team, refetch: refetchTeam, isLoading: teamLoading, error: teamError } = useQuery({
    queryKey: ['team', teamId],
    queryFn: async () => {
      const response = await teamApi.getTeam(Number(teamId));
      return response.data;
    },
    enabled: !!teamId,
    retry: 1,
    onError: (error) => {
      console.error('Error loading team:', error);
    },
  });

  const { data: members, isLoading: membersLoading, error: membersError } = useQuery({
    queryKey: ['team-members', teamId],
    queryFn: async () => {
      const response = await teamApi.getTeamMembers(Number(teamId));
      return response.data;
    },
    enabled: !!teamId,
    retry: 1,
    onError: (error) => {
      console.error('Error loading members:', error);
    },
  });

  const { data: contributions, refetch: refetchContributions, isLoading: contributionsLoading, error: contributionsError } = useQuery({
    queryKey: ['team-contributions', teamId, searchQuery, filterType, filterContributor, sortBy, sortOrder],
    queryFn: async () => {
      const params: any = {
        search: searchQuery || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (filterType !== 'all') {
        params.contribution_type = filterType;
      }
      if (filterContributor) {
        params.contributor_id = filterContributor;
      }
      const response = await contributionApi.getTeamContributions(Number(teamId), params);
      return response.data;
    },
    enabled: !!teamId,
    retry: 1,
    onError: (error) => {
      console.error('Error loading contributions:', error);
    },
  });

  const isLoading = teamLoading || membersLoading || contributionsLoading;
  const hasError = teamError || membersError || contributionsError;

  const handleVerify = async (contributionId: number) => {
    try {
      await verificationApi.verifyContribution(contributionId);
      refetchContributions();
    } catch (err: any) {
      console.error('Failed to verify:', err);
      alert(err.response?.data?.detail || 'Failed to verify contribution');
    }
  };

  const copyInviteCode = () => {
    if (team?.invite_code) {
      navigator.clipboard.writeText(team.invite_code);
      setCopiedInvite(true);
      setTimeout(() => setCopiedInvite(false), 2000);
    }
  };

  const handleArchiveTeam = async () => {
    if (!window.confirm('Are you sure you want to archive this team? This will freeze all contributions and prevent new ones.')) {
      return;
    }

    try {
      await teamApi.freezeTeam(Number(teamId));
      refetchTeam();
      alert('Team archived successfully!');
    } catch (err: any) {
      console.error('Failed to archive team:', err);
      alert(err.response?.data?.detail || 'Failed to archive team');
    }
  };

  if (teamLoading && !team) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600">Error loading team data</div>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600">Team not found</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">{team.name}</h1>
          {team.description && (
            <p className="text-gray-600 mb-4">{team.description}</p>
          )}
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{team.member_count} members</span>
            <span>•</span>
            <span className="capitalize">{team.status === 'frozen' ? 'Archived' : team.status}</span>
            <span>•</span>
            <div className="flex items-center gap-2">
              <code className="text-xs bg-gray-50 px-2 py-1 rounded font-mono">{team.invite_code}</code>
              <button
                onClick={copyInviteCode}
                className="text-gray-600 hover:text-gray-900"
                title="Copy invite code"
              >
                {copiedInvite ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {team.status === 'active' && (
            <Link
              to={`/teams/${teamId}/submit`}
              className="px-4 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 text-sm"
            >
              <Plus className="h-4 w-4 inline mr-1" />
              Submit
            </Link>
          )}
          {team.created_by === user?.id && team.status === 'active' && (
            <button
              onClick={handleArchiveTeam}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
            >
              Archive
            </button>
          )}
        </div>
      </div>

      {/* Members */}
      {members && members.length > 0 && (
        <div className="bg-white rounded border border-gray-100 p-4">
          <h2 className="text-sm font-medium text-gray-900 mb-3">Members</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {members.map((member) => {
              const isManager = team.created_by === user?.id;
              return (
                <Link
                  key={member.id}
                  to={`/teams/${teamId}/members/${member.id}`}
                  className="p-3 border border-gray-100 rounded hover:border-gray-300 transition"
                >
                  <div className="text-sm font-medium text-gray-900">{member.full_name || member.username}</div>
                  <div className="text-xs text-gray-500 mt-1">{member.username}</div>
                  {isManager && member.reputation && (
                    <div className="text-xs text-gray-600 mt-2">
                      {member.reputation.total_score?.toFixed(1) || '0.0'} pts
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400 text-sm"
        >
          <option value="all">All Types</option>
          <option value="git">Git</option>
          <option value="document">Document</option>
          <option value="image">Image</option>
          <option value="meeting">Meeting</option>
          <option value="mental">Mental</option>
          <option value="other">Other</option>
        </select>
        <select
          value={filterContributor || ''}
          onChange={(e) => setFilterContributor(e.target.value ? Number(e.target.value) : null)}
          className="px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400 text-sm"
        >
          <option value="">All Contributors</option>
          {members?.map((member) => (
            <option key={member.id} value={member.id}>
              {member.full_name || member.username}
            </option>
          ))}
        </select>
        <select
          value={`${sortBy}_${sortOrder}`}
          onChange={(e) => {
            const [by, order] = e.target.value.split('_');
            setSortBy(by);
            setSortOrder(order);
          }}
          className="px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400 text-sm"
        >
          <option value="created_at_desc">Newest</option>
          <option value="created_at_asc">Oldest</option>
          <option value="reputation_score_desc">Highest Score</option>
          <option value="reputation_score_asc">Lowest Score</option>
          <option value="verification_count_desc">Most Verified</option>
        </select>
      </div>

      {/* Contributions */}
      <div className="space-y-3">
        {!contributions || contributions.length === 0 ? (
          <div className="bg-white rounded border border-gray-100 p-12 text-center">
            <p className="text-gray-500">No contributions yet</p>
          </div>
        ) : (
          contributions.map((contribution) => (
            <div
              key={contribution.id}
              className="bg-white rounded border border-gray-100 p-4 hover:border-gray-300 transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium text-gray-900">{contribution.title}</h3>
                    <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-50 rounded">
                      {contribution.contribution_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-2">
                    {contribution.contributor.username} • {new Date(contribution.created_at).toLocaleDateString()}
                  </p>
                  {contribution.description && (
                    <p className="text-sm text-gray-700 mb-2">{contribution.description}</p>
                  )}
                  {contribution.external_link && (
                    <a
                      href={contribution.external_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-gray-600 hover:text-gray-900"
                    >
                      View link →
                    </a>
                  )}
                </div>
                <div className="text-right ml-4">
                  <div className="text-lg font-semibold text-gray-900">
                    {contribution.reputation_score.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-500">points</div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                <div className="text-sm text-gray-500">
                  <span>{contribution.verification_count} verifications</span>
                  {contribution.flag_count > 0 && (
                    <span className="ml-3 text-red-600">{contribution.flag_count} flags</span>
                  )}
                </div>
                {!contribution.verified_by_current_user && contribution.contributor_id !== user?.id && (
                  <button
                    onClick={() => handleVerify(contribution.id)}
                    className="px-3 py-1 bg-gray-50 text-gray-700 rounded hover:bg-gray-100 text-sm"
                  >
                    <Check className="h-4 w-4 inline mr-1" />
                    Verify
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
