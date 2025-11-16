import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { teamApi } from '../lib/api';

export function JoinTeam() {
  const navigate = useNavigate();
  const [inviteCode, setInviteCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await teamApi.joinTeam(inviteCode);
      navigate(`/teams/${response.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join team');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Join Team</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded border border-gray-100 p-6 space-y-5">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm text-gray-700 mb-1">Invite Code *</label>
          <input
            type="text"
            required
            value={inviteCode}
            onChange={(e) => setInviteCode(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400"
            placeholder="Enter invite code"
          />
          <p className="mt-2 text-xs text-gray-500">
            Ask your team instructor or manager for the invite code.
          </p>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 disabled:opacity-50"
          >
            {loading ? 'Joining...' : 'Join Team'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
