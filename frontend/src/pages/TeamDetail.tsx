import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi, verificationApi } from '../lib/api';
import { Users, FileText, Plus, Check, Flag, Copy, Archive, Search, Filter, ArrowUpDown } from 'lucide-react';
import type { Contribution, ContributionType } from '../types';
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

  // Show loading only if we don't have team data yet
  if (teamLoading && !team) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-gray-600">Loading team data...</div>
          {teamError && (
            <div className="text-sm text-red-600 mt-2">
              Error: {(teamError as any)?.response?.data?.detail || (teamError as any)?.message}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-red-600">Error loading team data. Please try refreshing the page.</div>
          <div className="text-sm text-gray-500 mt-2">
            {teamError && `Team: ${(teamError as any)?.response?.data?.detail || 'Unknown error'}`}
            {membersError && `Members: ${(membersError as any)?.response?.data?.detail || 'Unknown error'}`}
            {contributionsError && `Contributions: ${(contributionsError as any)?.response?.data?.detail || 'Unknown error'}`}
          </div>
        </div>
      </div>
    );
  }

  if (!team) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <div className="text-red-600">Team not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{team?.name}</h1>
            {team?.description && (
              <p className="text-gray-600 mt-2">{team.description}</p>
            )}
            <div className="mt-4 flex items-center space-x-4">
              <div className="flex items-center">
                <Users className="h-4 w-4 text-gray-500 mr-2" />
                <span className="text-sm text-gray-700">{team?.member_count} members</span>
              </div>
              <div className="flex items-center">
                <span className={`px-2 py-1 rounded text-xs ${
                  team?.status === 'active' ? 'bg-green-100 text-green-800' :
                  team?.status === 'frozen' ? 'bg-gray-100 text-gray-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {team?.status === 'frozen' ? 'Archived' : team?.status}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">Invite Code:</span>
                <code className="text-sm bg-gray-100 px-3 py-1 rounded text-gray-900 font-mono">
                  {team?.invite_code}
                </code>
                <button
                  onClick={copyInviteCode}
                  className="px-3 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100 flex items-center"
                  title="Copy invite code"
                >
                  {copiedInvite ? (
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
          <div className="flex gap-2">
            {team?.status === 'active' && (
              <Link
                to={`/teams/${teamId}/submit`}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Submit Contribution
              </Link>
            )}
            {team?.created_by === user?.id && team?.status === 'active' && (
              <button
                onClick={handleArchiveTeam}
                className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                <Archive className="h-4 w-4 mr-2" />
                Archive Team
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Members List */}
      {members && members.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Members</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {members.map((member) => {
              const isManager = team?.created_by === user?.id;
              return (
                <Link
                  key={member.id}
                  to={`/teams/${teamId}/members/${member.id}`}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{member.full_name || member.username}</h3>
                      <p className="text-sm text-gray-600">{member.username}</p>
                      <span className="text-xs text-gray-500 capitalize">{member.role}</span>
                    </div>
                    {isManager && member.reputation && (
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-900">
                          {member.reputation.total_score?.toFixed(1) || '0.0'}
                        </div>
                        <div className="text-xs text-gray-600">points</div>
                      </div>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search contributions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Filter by Type */}
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              <option value="git">Git</option>
              <option value="document">Document</option>
              <option value="image">Image</option>
              <option value="meeting">Meeting</option>
              <option value="mental">Mental</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Filter by Contributor */}
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-gray-500" />
            <select
              value={filterContributor || ''}
              onChange={(e) => setFilterContributor(e.target.value ? Number(e.target.value) : null)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Contributors</option>
              {members?.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.full_name || member.username}
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <ArrowUpDown className="h-4 w-4 text-gray-500" />
            <select
              value={`${sortBy}_${sortOrder}`}
              onChange={(e) => {
                const [by, order] = e.target.value.split('_');
                setSortBy(by);
                setSortOrder(order);
              }}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at_desc">Newest First</option>
              <option value="created_at_asc">Oldest First</option>
              <option value="reputation_score_desc">Highest Score</option>
              <option value="reputation_score_asc">Lowest Score</option>
              <option value="verification_count_desc">Most Verified</option>
              <option value="title_asc">Title (A-Z)</option>
              <option value="title_desc">Title (Z-A)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Contributions Feed */}
      <div className="space-y-4">
        {!contributions || contributions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No contributions yet. Be the first to contribute!</p>
          </div>
        ) : (
          contributions.map((contribution) => (
            <div
              key={contribution.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {contribution.title}
                    </h3>
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                      {contribution.contribution_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    by {contribution.contributor.username} • {new Date(contribution.created_at).toLocaleString()}
                  </p>
                  {contribution.description && (
                    <p className="text-gray-700 mt-3">{contribution.description}</p>
                  )}
                  {contribution.external_link && (
                    <a
                      href={contribution.external_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm mt-2 inline-block"
                    >
                      View external link →
                    </a>
                  )}
                </div>

                <div className="text-right ml-4">
                  <div className="text-2xl font-bold text-gray-900">
                    {contribution.reputation_score.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-600">points</div>
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-gray-200 pt-4">
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span className="flex items-center">
                    <Check className="h-4 w-4 mr-1" />
                    {contribution.verification_count} verifications
                  </span>
                  {contribution.flag_count > 0 && (
                    <span className="flex items-center text-red-600">
                      <Flag className="h-4 w-4 mr-1" />
                      {contribution.flag_count} flags
                    </span>
                  )}
                </div>

                {!contribution.verified_by_current_user && contribution.contributor_id !== user?.id && (
                  <button
                    onClick={() => handleVerify(contribution.id)}
                    className="inline-flex items-center px-3 py-1 bg-green-50 text-green-700 rounded-md hover:bg-green-100 text-sm font-medium"
                  >
                    <Check className="h-4 w-4 mr-1" />
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
