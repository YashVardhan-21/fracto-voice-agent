import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { scrapeJobs, runBatch } from '../api/companies';
import { Header } from '../components/layout/Header';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import toast from 'react-hot-toast';

export function Pipeline() {
  const [keywords, setKeywords] = useState('receptionist');
  const [location, setLocation] = useState('Dublin, Ireland');
  const [limit, setLimit] = useState(20);
  const [lastResult, setLastResult] = useState<{ scraped: number; new_companies: number } | null>(null);
  const qc = useQueryClient();

  const scrape = useMutation({
    mutationFn: () => scrapeJobs(keywords, location, limit),
    onSuccess: (data) => {
      setLastResult(data);
      toast.success(`Scraped ${data.scraped} jobs, added ${data.new_companies} new companies`);
      qc.invalidateQueries({ queryKey: ['companies'] });
    },
    onError: () => toast.error('Scraping failed'),
  });

  const batch = useMutation({
    mutationFn: runBatch,
    onSuccess: (data) => {
      toast.success(`Queued ${data.queued} companies for analysis`);
      qc.invalidateQueries({ queryKey: ['companies'] });
    },
    onError: () => toast.error('Batch failed'),
  });

  return (
    <>
      <Header title="Pipeline" />
      <div className="p-8 space-y-6 max-w-2xl">
        <Card>
          <h2 className="font-semibold text-gray-900 mb-1">Step 1 — Scrape Jobs from Indeed</h2>
          <p className="text-sm text-gray-500 mb-4">
            Find companies currently hiring receptionists — prime prospects for voice agent outreach.
          </p>
          <div className="space-y-3">
            <Input
              label="Job Keywords"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
            <Input
              label="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
            <Input
              label="Max Results"
              type="number"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
            />
            <Button onClick={() => scrape.mutate()} loading={scrape.isPending}>
              Scrape Indeed
            </Button>
          </div>
          {lastResult && (
            <div className="mt-4 p-3 bg-green-50 rounded-lg text-sm text-green-800">
              ✓ Found {lastResult.scraped} jobs · Added {lastResult.new_companies} new companies
            </div>
          )}
        </Card>

        <Card>
          <h2 className="font-semibold text-gray-900 mb-1">Step 2 — Analyse & Create Agents</h2>
          <p className="text-sm text-gray-500 mb-4">
            Runs website analysis + prompt generation + VAPI agent creation for all pending companies (batch of 10).
          </p>
          <Button variant="secondary" onClick={() => batch.mutate()} loading={batch.isPending}>
            Run Batch Pipeline
          </Button>
        </Card>
      </div>
    </>
  );
}
