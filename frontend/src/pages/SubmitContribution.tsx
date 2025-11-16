import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { contributionApi } from '../lib/api';
import { ContributionType } from '../types';

export function SubmitContribution() {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    contribution_type: ContributionType.OTHER,
    external_link: '',
    self_assessed_impact: 3,
  });
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = new FormData();
      data.append('title', formData.title);
      data.append('description', formData.description);
      data.append('contribution_type', formData.contribution_type);
      data.append('team_id', teamId!);
      data.append('self_assessed_impact', formData.self_assessed_impact.toString());

      if (formData.external_link) {
        data.append('external_link', formData.external_link);
      }

      if (file) {
        data.append('file', file);
      }

      await contributionApi.createContribution(data);
      navigate(`/teams/${teamId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit contribution');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Submit Contribution</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded border border-gray-100 p-6 space-y-5">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm text-gray-700 mb-1">Title *</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400"
            placeholder="Brief description"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-700 mb-1">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400"
            placeholder="Detailed explanation"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-700 mb-1">Type *</label>
          <select
            value={formData.contribution_type}
            onChange={(e) => setFormData({ ...formData, contribution_type: e.target.value as ContributionType })}
            className="w-full px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400"
          >
            <option value={ContributionType.GIT}>Git Commit</option>
            <option value={ContributionType.DOCUMENT}>Document</option>
            <option value={ContributionType.IMAGE}>Image/Handwritten Notes</option>
            <option value={ContributionType.MEETING}>Meeting/Discussion</option>
            <option value={ContributionType.MENTAL}>Mental Contribution</option>
            <option value={ContributionType.OTHER}>Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-700 mb-1">External Link</label>
          <input
            type="url"
            value={formData.external_link}
            onChange={(e) => setFormData({ ...formData, external_link: e.target.value })}
            className="w-full px-3 py-2 border border-gray-200 rounded focus:outline-none focus:border-gray-400"
            placeholder="https://..."
          />
        </div>

        <div>
          <label className="block text-sm text-gray-700 mb-2">
            Upload File (Optional)
          </label>
          <label className="flex items-center justify-center w-full h-24 border-2 border-gray-200 border-dashed rounded cursor-pointer hover:border-gray-300">
            <div className="text-center">
              <p className="text-sm text-gray-600">
                {file ? file.name : 'Click to upload or drag and drop'}
              </p>
              <p className="text-xs text-gray-500 mt-1">PDF, PNG, JPG, TXT, etc.</p>
            </div>
            <input
              type="file"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </label>
        </div>

        <div>
          <label className="block text-sm text-gray-700 mb-2">
            Impact: {formData.self_assessed_impact}
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={formData.self_assessed_impact}
            onChange={(e) => setFormData({ ...formData, self_assessed_impact: Number(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit'}
          </button>
          <button
            type="button"
            onClick={() => navigate(`/teams/${teamId}`)}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
