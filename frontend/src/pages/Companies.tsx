import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCompanies, runPipeline } from '../api/companies';
import { Header } from '../components/layout/Header';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import toast from 'react-hot-toast';

export function Companies() {
  const [search, setSearch] = useState('');
  const qc = useQueryClient();

  const { data: companies = [], isLoading } = useQuery({
    queryKey: ['companies', search],
    queryFn: () => getCompanies({ search: search || undefined }),
  });

  const pipeline = useMutation({
    mutationFn: runPipeline,
    onSuccess: () => {
      toast.success('Pipeline started');
      qc.invalidateQueries({ queryKey: ['companies'] });
    },
    onError: () => toast.error('Failed to start pipeline'),
  });

  return (
    <>
      <Header title="Companies" />
      <div className="p-8 space-y-4">
        <div className="flex gap-3 items-center justify-between">
          <Input
            placeholder="Search companies…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-64"
          />
          <span className="text-sm text-gray-500">{companies.length} companies</span>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['Company', 'Type', 'Location', 'Score', 'Status', ''].map((h) => (
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
                  <td colSpan={6} className="text-center py-8 text-gray-400">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && companies.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-gray-400">
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
                  <td className="px-4 py-3">
                    {c.analysis_score != null
                      ? `${Math.round(c.analysis_score * 100)}%`
                      : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <Badge label={c.status} status={c.status} />
                  </td>
                  <td className="px-4 py-3">
                    {c.status === 'pending' && (
                      <Button
                        size="sm"
                        variant="secondary"
                        loading={pipeline.isPending}
                        onClick={() => pipeline.mutate(c.id)}
                      >
                        Run Pipeline
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
