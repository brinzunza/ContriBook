import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { reputationApi } from '../lib/api';
import { Award, Trophy, Medal } from 'lucide-react';

export function Leaderboard() {
  const { teamId } = useParams<{ teamId: string }>();

  const { data: leaderboard } = useQuery({
    queryKey: ['leaderboard', teamId],
    queryFn: async () => {
      const response = await reputationApi.getTeamLeaderboard(Number(teamId));
      return response.data;
    },
  });

  const getRankIcon = (index: number) => {
    if (index === 0) return <Trophy className="h-6 w-6 text-yellow-500" />;
    if (index === 1) return <Medal className="h-6 w-6 text-gray-400" />;
    if (index === 2) return <Medal className="h-6 w-6 text-orange-600" />;
    return <Award className="h-6 w-6 text-gray-300" />;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">
        {leaderboard?.team_name} Leaderboard
      </h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Rankings</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {leaderboard?.rankings.map((entry, index) => (
            <div key={entry.user.id} className="p-6 flex items-center space-x-4 hover:bg-gray-50">
              <div className="flex-shrink-0 w-8 flex justify-center">
                {getRankIcon(index)}
              </div>

              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-gray-900">
                    {entry.user.full_name || entry.user.username}
                  </h3>
                  <span className={`px-2 py-1 text-xs rounded ${
                    entry.user.role === 'instructor' || entry.user.role === 'manager'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {entry.user.role}
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Contributions</p>
                    <p className="font-medium text-gray-900">
                      {entry.reputation.total_contributions}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Verified</p>
                    <p className="font-medium text-green-600">
                      {entry.reputation.verified_contributions}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Instructor ✓</p>
                    <p className="font-medium text-blue-600">
                      {entry.reputation.instructor_verified}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Flagged</p>
                    <p className="font-medium text-red-600">
                      {entry.reputation.flagged_contributions}
                    </p>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">
                  {entry.reputation.total_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">points</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
