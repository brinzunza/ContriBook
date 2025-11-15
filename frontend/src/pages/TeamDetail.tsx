import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi, reputationApi, verificationApi } from '../lib/api';
import { Users, FileText, Award, Plus, Check, Flag } from 'lucide-react';
import type { Contribution } from '../types';

export function TeamDetail() {
  const { teamId } = useParams<{ teamId: string }>();
  const [showSubmitForm, setShowSubmitForm] = useState(false);

  const { data: team } = useQuery({
    queryKey: ['team', teamId],
    queryFn: async () => {
      const response = await teamApi.getTeam(Number(teamId));
      return response.data;
    },
  });

  const { data: contributions, refetch: refetchContributions } = useQuery({
    queryKey: ['team-contributions', teamId],
    queryFn: async () => {
      const response = await contributionApi.getTeamContributions(Number(teamId));
      return response.data;
    },
  });

  const { data: leaderboard } = useQuery({
    queryKey: ['leaderboard', teamId],
    queryFn: async () => {
      const response = await reputationApi.getTeamLeaderboard(Number(teamId));
      return response.data;
    },
  });

  const handleVerify = async (contributionId: number) => {
    try {
      await verificationApi.verifyContribution(contributionId);
      refetchContributions();
    } catch (err) {
      console.error('Failed to verify:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{team?.name}</h1>
          {team?.description && (
            <p className="text-gray-600 mt-2">{team.description}</p>
          )}
        </div>
        <Link
          to={`/teams/${teamId}/submit`}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Submit Contribution
        </Link>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button className="py-4 px-1 border-b-2 border-blue-600 text-blue-600 font-medium">
            Feed
          </button>
          <Link
            to={`/teams/${teamId}/leaderboard`}
            className="py-4 px-1 border-b-2 border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300 font-medium"
          >
            Leaderboard
          </Link>
        </nav>
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

                {!contribution.verified_by_current_user && (
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
