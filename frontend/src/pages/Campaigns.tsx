import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCampaigns, createCampaign } from '../api/campaigns';
import { Header } from '../components/layout/Header';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';
import toast from 'react-hot-toast';

const TH_CLS =
  'text-left px-4 py-3 text-[11px] font-sf-mono uppercase tracking-[0.05em] text-steel-grey';
const TD_CLS = 'px-4 py-3';

export function Campaigns() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const qc = useQueryClient();

  const { data: campaigns = [], isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: getCampaigns,
  });

  const create = useMutation({
    mutationFn: () => createCampaign({ name, description }),
    onSuccess: () => {
      toast.success('Campaign created');
      setOpen(false);
      setName('');
      setDescription('');
      qc.invalidateQueries({ queryKey: ['campaigns'] });
    },
    onError: () => toast.error('Failed to create campaign'),
  });

  return (
    <>
      <Header title="Campaigns" />
      <div className="p-4 sm:p-6 space-y-3">
        <div className="flex justify-end">
          <Button onClick={() => setOpen(true)}>New Campaign</Button>
        </div>

        <div className="bg-display-black border border-digital-white/10 rounded-lg overflow-x-auto">
          <table className="w-full min-w-[560px] text-sm">
            <thead className="border-b border-digital-white/10">
              <tr>
                {['Name', 'Status', 'Created'].map((h) => (
                  <th key={h} className={TH_CLS}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={3} className="text-center py-10 text-slate-blue text-[12px] font-sf-mono">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && campaigns.length === 0 && (
                <tr>
                  <td colSpan={3} className="text-center py-10 text-slate-blue text-[12px] font-sf-mono">
                    No campaigns yet.
                  </td>
                </tr>
              )}
              {campaigns.map((c) => (
                <tr
                  key={c.id}
                  className="border-b border-digital-white/[0.06] hover:bg-digital-white/[0.03] transition-colors"
                >
                  <td className={`${TD_CLS} font-medium text-digital-white text-[13px]`}>{c.name}</td>
                  <td className={TD_CLS}>
                    <Badge label={c.status} status={c.status} />
                  </td>
                  <td className={`${TD_CLS} text-slate-blue text-[12px] font-sf-mono`}>
                    {new Date(c.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="New Campaign">
        <div className="space-y-4">
          <Input
            label="Campaign Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Dublin Dental Outreach Q1"
            required
          />
          <Input
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description"
          />
          <div className="flex gap-2 justify-end pt-1">
            <Button variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => create.mutate()} loading={create.isPending} disabled={!name}>
              Create Campaign
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
