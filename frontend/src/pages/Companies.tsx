import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCompanies, getTopLeads, reanalyzeCompanies, runPipeline } from '../api/companies';
import { Header } from '../components/layout/Header';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import toast from 'react-hot-toast';

export function Companies() {
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState<'all' | 'top'>('top');
  const qc = useQueryClient();

  const { data: companies = [], isLoading } = useQuery({
    queryKey: ['companies', viewMode, search],
    queryFn: () =>
      viewMode === 'top'
        ? getTopLeads({ search: search || undefined, limit: 50 })
        : getCompanies({ search: search || undefined }),
  });

  const pipeline = useMutation({
    mutationFn: runPipeline,
    onSuccess: () => {
      toast.success('Pipeline started');
      qc.invalidateQueries({ queryKey: ['companies'] });
    },
    onError: () => toast.error('Failed to start pipeline'),
  });

  const reanalyze = useMutation({
    mutationFn: (mode: 'top' | 'all') => reanalyzeCompanies(mode, 50),
    onSuccess: (data) => {
      toast.success(`Queued ${data?.queued ?? 0} companies for re-analysis`);
      qc.invalidateQueries({ queryKey: ['companies'] });
    },
    onError: () => toast.error('Failed to queue re-analysis'),
  });

  const formatScore = (score?: number) => {
    if (score == null) return '—';
    const normalized = score <= 1 ? score * 100 : score;
    return `${Math.round(normalized)}%`;
  };

  const qualityMeta = (score?: number) => {
    if (score == null) return { label: 'Unknown', className: 'bg-gray-100 text-gray-700' };
    if (score < 55) return { label: 'Low', className: 'bg-red-100 text-red-700' };
    if (score < 75) return { label: 'Medium', className: 'bg-yellow-100 text-yellow-700' };
    return { label: 'High', className: 'bg-green-100 text-green-700' };
  };

  const upsellMeta = (website?: string, score?: number, issues?: string[]) => {
    const hasIssues = Array.isArray(issues) && issues.length >= 2;
    const shouldUpsell = !website || (score ?? 100) < 55 || hasIssues;
    return shouldUpsell
      ? { label: 'Yes', className: 'bg-purple-100 text-purple-700' }
      : { label: 'No', className: 'bg-gray-100 text-gray-700' };
  };

  return (
    <>
      <Header title="Companies" />
      <div className="p-8 space-y-4">
        <div className="flex gap-3 items-center justify-between">
          <div className="flex gap-3 items-center">
            <Input
              placeholder="Search companies…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-64"
            />
            <div className="flex rounded-lg border border-gray-200 overflow-hidden">
              <button
                type="button"
                onClick={() => setViewMode('top')}
                className={`px-3 py-2 text-xs font-medium ${
                  viewMode === 'top'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Top Leads
              </button>
              <button
                type="button"
                onClick={() => setViewMode('all')}
                className={`px-3 py-2 text-xs font-medium border-l border-gray-200 ${
                  viewMode === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                All Companies
              </button>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              size="sm"
              variant="secondary"
              loading={reanalyze.isPending}
              onClick={() => reanalyze.mutate(viewMode)}
            >
              {viewMode === 'top' ? 'Re-analyze Top Leads' : 'Re-analyze Companies'}
            </Button>
            <span className="text-sm text-gray-500">{companies.length} companies</span>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {[
                  'Company',
                  'Type',
                  'Location',
                  'Score',
                  'Website Quality',
                  'Upsell Opportunity',
                  'Status',
                  '',
                ].map((h) => (
                  <th
                    key={h}
                    className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading && (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-gray-400">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && companies.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-gray-400">
                    No companies yet. Run the pipeline to get started.
                  </td>
                </tr>
              )}
              {companies.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.name}</td>
                  <td className="px-4 py-3 text-gray-500 capitalize">
                    {c.business_type ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{c.location ?? '—'}</td>
                  <td className="px-4 py-3">{formatScore(c.analysis_score)}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        qualityMeta(c.website_quality_score).className
                      }`}
                    >
                      {qualityMeta(c.website_quality_score).label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        upsellMeta(c.website, c.website_quality_score, c.website_quality_issues).className
                      }`}
                    >
                      {upsellMeta(c.website, c.website_quality_score, c.website_quality_issues).label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge label={c.status} status={c.status} />
                  </td>
                  <td className="px-4 py-3">
                    {(c.status === 'pending' || c.status === 'vapi_failed') && (
                      <Button
                        size="sm"
                        variant="secondary"
                        loading={pipeline.isPending}
                        onClick={() => pipeline.mutate(c.id)}
                      >
                        {c.status === 'vapi_failed' ? 'Retry Pipeline' : 'Run Pipeline'}
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
