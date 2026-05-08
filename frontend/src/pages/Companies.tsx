import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCompanies, getTopLeads, reanalyzeCompanies, runPipeline } from '../api/companies';
import { downloadCompaniesAsXlsx } from '../utils/companyExport';
import { Header } from '../components/layout/Header';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import toast from 'react-hot-toast';

const TH_CLS =
  'text-left px-4 py-3 text-[11px] font-sf-mono uppercase tracking-[0.05em] text-steel-grey';
const TD_CLS = 'px-4 py-3';

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

  const qualityBadgeProps = (score?: number): { label: string; status: string } => {
    if (score == null) return { label: 'Unknown', status: 'draft' };
    if (score < 55) return { label: 'Low', status: 'vapi_failed' };
    if (score < 75) return { label: 'Medium', status: 'paused' };
    return { label: 'High', status: 'active' };
  };

  const upsellBadgeProps = (
    website?: string,
    score?: number,
    issues?: string[]
  ): { label: string; status: string } => {
    const hasIssues = Array.isArray(issues) && issues.length >= 2;
    const shouldUpsell = !website || (score ?? 100) < 55 || hasIssues;
    return shouldUpsell
      ? { label: 'Yes', status: 'analyzing' }
      : { label: 'No', status: 'draft' };
  };

  return (
    <>
      <Header title="Companies" />
      <div className="p-4 sm:p-6 space-y-3">
        {/* Toolbar */}
        <div className="flex gap-2 items-center flex-wrap justify-between">
          <div className="flex gap-2 items-center flex-wrap">
            <div className="relative">
              <Input
                placeholder="Search companies…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full sm:w-56 text-[12px]"
              />
            </div>
            <div className="flex border border-digital-white/20 rounded-buttons overflow-hidden">
              {(['top', 'all'] as const).map((m, i) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setViewMode(m)}
                  className={[
                    'px-3 py-1.5 text-[11px] font-sf-mono uppercase tracking-[0.04em] transition-colors',
                    i > 0 ? 'border-l border-digital-white/20' : '',
                    viewMode === m
                      ? 'bg-urgency-red text-digital-white'
                      : 'bg-transparent text-steel-grey hover:text-digital-white',
                  ].join(' ')}
                >
                  {m === 'top' ? 'Top Leads' : 'All Companies'}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
            <Button
              size="sm"
              variant="secondary"
              disabled={isLoading || companies.length === 0}
              onClick={() => {
                try {
                  downloadCompaniesAsXlsx(companies, viewMode, search);
                  toast.success('Excel file downloaded');
                } catch {
                  toast.error('Export failed');
                }
              }}
            >
              Export Excel
            </Button>
            <Button
              size="sm"
              variant="secondary"
              loading={reanalyze.isPending}
              onClick={() => reanalyze.mutate(viewMode)}
            >
              {viewMode === 'top' ? 'Re-analyze Top Leads' : 'Re-analyze Companies'}
            </Button>
            <span className="text-[11px] text-steel-grey font-sf-mono">{companies.length} companies</span>
          </div>
        </div>

        {/* Table */}
        <div className="bg-display-black border border-digital-white/10 rounded-lg overflow-x-auto">
          <table className="w-full min-w-[980px] text-sm">
            <thead className="border-b border-digital-white/10">
              <tr>
                {['Company', 'Type', 'Location', 'Email', 'Score', 'Website Quality', 'Upsell', 'Status', ''].map(
                  (h) => (
                    <th key={h} className={TH_CLS}>
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={9} className="text-center py-10 text-slate-blue text-[12px] font-sf-mono">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && companies.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center py-10 text-slate-blue text-[12px] font-sf-mono">
                    No companies yet. Run the pipeline to get started.
                  </td>
                </tr>
              )}
              {companies.map((c) => (
                <tr
                  key={c.id}
                  className="border-b border-digital-white/[0.06] hover:bg-digital-white/[0.03] transition-colors"
                >
                  <td className={`${TD_CLS} font-medium text-digital-white text-[13px]`}>{c.name}</td>
                  <td className={`${TD_CLS} text-slate-blue text-[12px] capitalize`}>
                    {c.business_type ?? '—'}
                  </td>
                  <td className={`${TD_CLS} text-slate-blue text-[12px]`}>{c.location ?? '—'}</td>
                  <td
                    className={`${TD_CLS} text-slate-blue text-[12px] max-w-[180px] truncate`}
                    title={c.email ?? undefined}
                  >
                    {c.email ?? '—'}
                  </td>
                  <td className={`${TD_CLS} text-digital-white text-[12px] font-sf-mono`}>
                    {formatScore(c.analysis_score)}
                  </td>
                  <td className={TD_CLS}>
                    <Badge {...qualityBadgeProps(c.website_quality_score)} />
                  </td>
                  <td className={TD_CLS}>
                    <Badge {...upsellBadgeProps(c.website, c.website_quality_score, c.website_quality_issues)} />
                  </td>
                  <td className={TD_CLS}>
                    <Badge label={c.status} status={c.status} />
                  </td>
                  <td className={TD_CLS}>
                    {(c.status === 'pending' || c.status === 'vapi_failed') && (
                      <Button
                        size="sm"
                        loading={pipeline.isPending}
                        onClick={() => pipeline.mutate(c.id)}
                      >
                        {c.status === 'vapi_failed' ? 'Retry' : 'Run Pipeline'}
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
