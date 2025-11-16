import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi } from '../lib/api';
import { ArrowLeft, FileText, Check, Flag } from 'lucide-react';
import type { Contribution } from '../types';

export function MemberContributions() {
  const { teamId, memberId } = useParams<{ teamId: string; memberId: string }>();

  const { data: team } = useQuery({
    queryKey: ['team', teamId],
    queryFn: async () => {
      const response = await teamApi.getTeam(Number(teamId));
      return response.data;
    },
  });

  const { data: members } = useQuery({
    queryKey: ['team-members', teamId],
    queryFn: async () => {
      const response = await teamApi.getTeamMembers(Number(teamId));
      return response.data;
    },
  });

  const member = members?.find((m) => m.id === Number(memberId));

  const { data: contributions } = useQuery({
    queryKey: ['member-contributions', teamId, memberId],
    queryFn: async () => {
      const response = await contributionApi.getTeamContributions(Number(teamId), {
        contributor_id: Number(memberId),
      });
      return response.data;
    },
  });

  const totalScore = contributions?.reduce((sum, c) => sum + c.reputation_score, 0) || 0;
  const totalContributions = contributions?.length || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <Link
          to={`/teams/${teamId}`}
          className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Team
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">
          {member?.full_name || member?.username}'s Contributions
        </h1>
        {team && (
          <p className="text-gray-600 mt-2">
            Team: <span className="font-medium">{team.name}</span>
          </p>
        )}
        <div className="mt-4 flex items-center space-x-6">
          <div>
            <div className="text-2xl font-bold text-gray-900">{totalContributions}</div>
            <div className="text-sm text-gray-600">Total Contributions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{totalScore.toFixed(1)}</div>
            <div className="text-sm text-gray-600">Total Score</div>
          </div>
        </div>
      </div>

      {/* Contributions List */}
      <div className="space-y-4">
        {!contributions || contributions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No contributions yet.</p>
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
                    {new Date(contribution.created_at).toLocaleString()}
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

              <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600 border-t border-gray-200 pt-4">
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
            </div>
          ))
        )}
      </div>
    </div>
  );
}

