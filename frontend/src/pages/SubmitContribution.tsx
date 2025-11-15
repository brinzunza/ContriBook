import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { contributionApi } from '../lib/api';
import { ContributionType } from '../types';
import { Upload, Link as LinkIcon } from 'lucide-react';

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
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Submit Contribution</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Title *
          </label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Brief description of your contribution"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Detailed explanation of what you contributed"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Type *
          </label>
          <select
            value={formData.contribution_type}
            onChange={(e) => setFormData({ ...formData, contribution_type: e.target.value as ContributionType })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
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
          <label className="block text-sm font-medium text-gray-700">
            External Link
          </label>
          <div className="mt-1 flex rounded-md shadow-sm">
            <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500">
              <LinkIcon className="h-4 w-4" />
            </span>
            <input
              type="url"
              value={formData.external_link}
              onChange={(e) => setFormData({ ...formData, external_link: e.target.value })}
              className="flex-1 block w-full px-3 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://github.com/... or https://docs.google.com/..."
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload File (Optional)
          </label>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="h-8 w-8 text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">
                  {file ? file.name : 'Click to upload or drag and drop'}
                </p>
                <p className="text-xs text-gray-500">PDF, PNG, JPG, TXT, etc.</p>
              </div>
              <input
                type="file"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Self-Assessed Impact: {formData.self_assessed_impact}
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={formData.self_assessed_impact}
            onChange={(e) => setFormData({ ...formData, self_assessed_impact: Number(e.target.value) })}
            className="mt-2 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
          </div>
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit Contribution'}
          </button>
          <button
            type="button"
            onClick={() => navigate(`/teams/${teamId}`)}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
