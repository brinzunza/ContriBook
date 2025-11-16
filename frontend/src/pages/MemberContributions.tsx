import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { teamApi, contributionApi } from '../lib/api';
import { ArrowLeft } from 'lucide-react';

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
      <div className="flex items-center gap-4">
        <Link
          to={`/teams/${teamId}`}
          className="text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-gray-900">
            {member?.full_name || member?.username}'s Contributions
          </h1>
          {team && (
            <p className="text-sm text-gray-500 mt-1">{team.name}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Contributions</p>
          <p className="text-2xl font-semibold text-gray-900">{totalContributions}</p>
        </div>
        <div className="bg-white p-4 rounded border border-gray-100">
          <p className="text-xs text-gray-500 mb-1">Total Score</p>
          <p className="text-2xl font-semibold text-gray-900">{totalScore.toFixed(1)}</p>
        </div>
      </div>

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
                    {new Date(contribution.created_at).toLocaleDateString()}
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

              <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-500">
                <span>{contribution.verification_count} verifications</span>
                {contribution.flag_count > 0 && (
                  <span className="ml-3 text-red-600">{contribution.flag_count} flags</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
