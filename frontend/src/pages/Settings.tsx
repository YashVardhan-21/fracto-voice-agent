import { FormEvent, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { Header } from '../components/layout/Header';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { createTeamUser, getTeamUsers, updateTeamUser, type TeamRole } from '../api/team';
import { getIntegrations, updateIntegrations } from '../api/settings';
import { useAuthStore } from '../store/authStore';
import { Badge } from '../components/ui/Badge';

type SettingsTab = 'team' | 'integrations';

const TH_CLS =
  'text-left px-4 py-3 text-[11px] font-sf-mono uppercase tracking-[0.05em] text-steel-grey';
const TD_CLS = 'px-4 py-3';

const SECTION_TITLE = 'text-[12px] uppercase tracking-[0.06em] font-sf-mono text-digital-white mb-4';

const SELECT_CLS =
  'mt-1 h-10 w-full rounded-buttons border border-steel-grey/50 bg-display-black text-digital-white px-4 text-[13px] focus:outline-none focus:ring-2 focus:ring-active-blue';

export function Settings() {
  const user = useAuthStore((s) => s.user);
  const [tab, setTab] = useState<SettingsTab>('team');
  const isAdmin = Boolean(user?.is_admin) || user?.role === 'admin';

  if (!isAdmin) {
    return (
      <>
        <Header title="Settings" />
        <div className="p-6 text-[12px] text-slate-blue font-sf-mono">Admin access required.</div>
      </>
    );
  }

  return (
    <>
      <Header title="Settings" />
      <div className="p-4 sm:p-6 space-y-4">
        {/* Tabs */}
        <div className="flex border border-digital-white/20 rounded-buttons overflow-hidden w-fit">
          {(['team', 'integrations'] as SettingsTab[]).map((t, i) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={[
                'px-5 py-2 text-[11px] font-sf-mono uppercase tracking-[0.05em] transition-colors',
                i > 0 ? 'border-l border-digital-white/20' : '',
                tab === t
                  ? 'bg-urgency-red text-digital-white'
                  : 'bg-transparent text-steel-grey hover:text-digital-white',
              ].join(' ')}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === 'team' ? (
          <TeamTab thCls={TH_CLS} tdCls={TD_CLS} sectionTitle={SECTION_TITLE} selectCls={SELECT_CLS} />
        ) : (
          <IntegrationsTab sectionTitle={SECTION_TITLE} />
        )}
      </div>
    </>
  );
}

function TeamTab({
  thCls,
  tdCls,
  sectionTitle,
  selectCls,
}: {
  thCls: string;
  tdCls: string;
  sectionTitle: string;
  selectCls: string;
}) {
  const qc = useQueryClient();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<TeamRole>('agent');
  const [temporaryPassword, setTemporaryPassword] = useState('');

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['team-users'],
    queryFn: getTeamUsers,
  });

  const createUser = useMutation({
    mutationFn: createTeamUser,
    onSuccess: () => {
      toast.success('Team user created');
      setEmail('');
      setFullName('');
      setRole('agent');
      setTemporaryPassword('');
      qc.invalidateQueries({ queryKey: ['team-users'] });
    },
    onError: () => toast.error('Unable to create user'),
  });

  const toggleActive = useMutation({
    mutationFn: ({ userId, isActive }: { userId: number; isActive: boolean }) =>
      updateTeamUser(userId, { is_active: isActive }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['team-users'] }),
    onError: () => toast.error('Unable to update user status'),
  });

  const handleCreate = (e: FormEvent) => {
    e.preventDefault();
    createUser.mutate({ email, full_name: fullName, role, temporary_password: temporaryPassword });
  };

  return (
    <div className="space-y-3">
      {/* Add user form */}
      <div className="bg-display-black border border-digital-white/10 rounded-lg p-4">
        <h2 className={sectionTitle}>Add Team User</h2>
        <form className="grid grid-cols-1 md:grid-cols-2 gap-3" onSubmit={handleCreate}>
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input
            label="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
          <label className="flex flex-col gap-1">
            <span className="text-[11px] uppercase tracking-[0.05em] text-digital-white font-sf-mono">Role</span>
            <select className={selectCls} value={role} onChange={(e) => setRole(e.target.value as TeamRole)}>
              <option value="agent">agent</option>
              <option value="manager">manager</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <Input
            label="Temporary password"
            type="password"
            value={temporaryPassword}
            onChange={(e) => setTemporaryPassword(e.target.value)}
            required
          />
          <div className="md:col-span-2">
            <Button type="submit" loading={createUser.isPending}>
              Create User
            </Button>
          </div>
        </form>
      </div>

      {/* Team table */}
      <div className="bg-display-black border border-digital-white/10 rounded-lg overflow-x-auto">
        <table className="w-full min-w-[780px] text-sm">
          <thead className="border-b border-digital-white/10">
            <tr>
              {['Name', 'Email', 'Role', 'Admin', 'Status', ''].map((h) => (
                <th key={h} className={thCls}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td className="px-4 py-10 text-center text-slate-blue text-[12px] font-sf-mono" colSpan={6}>
                  Loading team…
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr
                  key={u.id}
                  className="border-b border-digital-white/[0.06] hover:bg-digital-white/[0.03] transition-colors"
                >
                  <td className={`${tdCls} font-medium text-digital-white text-[13px]`}>{u.full_name}</td>
                  <td className={`${tdCls} text-slate-blue text-[12px]`}>{u.email}</td>
                  <td className={`${tdCls} text-slate-blue text-[12px] font-sf-mono uppercase`}>{u.role}</td>
                  <td className={`${tdCls} text-slate-blue text-[12px]`}>{u.is_admin ? 'Yes' : 'No'}</td>
                  <td className={tdCls}>
                    <Badge
                      label={u.is_active ? 'Active' : 'Inactive'}
                      status={u.is_active ? 'active' : 'draft'}
                    />
                  </td>
                  <td className={tdCls}>
                    <Button
                      size="sm"
                      variant={u.is_active ? 'danger' : 'primary'}
                      loading={toggleActive.isPending}
                      onClick={() => toggleActive.mutate({ userId: u.id, isActive: !u.is_active })}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function IntegrationsTab({ sectionTitle }: { sectionTitle: string }) {
  const [vapiApiKey, setVapiApiKey] = useState('');
  const [vapiVoiceId, setVapiVoiceId] = useState('');
  const [vapiPhoneId, setVapiPhoneId] = useState('');
  const [googlePlaces, setGooglePlaces] = useState('');
  const [adzunaAppId, setAdzunaAppId] = useState('');
  const [adzunaAppKey, setAdzunaAppKey] = useState('');
  const [adzunaCountry, setAdzunaCountry] = useState('gb');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [deepseekKey, setDeepseekKey] = useState('');

  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ['settings-integrations'],
    queryFn: getIntegrations,
  });

  const configuredSummary = useMemo(() => {
    if (!data) return [];
    return [
      ['VAPI API key', data.vapi?.api_key?.configured],
      ['OpenAI key', data.llm?.openai_api_key?.configured],
      ['Gemini key', data.llm?.gemini_api_key?.configured],
      ['Deepseek key', data.llm?.deepseek_api_key?.configured],
      ['Google Places key', data.leads?.google_places_api_key?.configured],
      ['Adzuna App ID', data.leads?.adzuna_app_id?.configured],
      ['Adzuna App Key', data.leads?.adzuna_app_key?.configured],
    ] as Array<[string, boolean | undefined]>;
  }, [data]);

  const save = useMutation({
    mutationFn: updateIntegrations,
    onSuccess: () => {
      toast.success('Integrations updated');
      qc.invalidateQueries({ queryKey: ['settings-integrations'] });
      setVapiApiKey('');
      setGooglePlaces('');
      setAdzunaAppId('');
      setAdzunaAppKey('');
      setOpenaiKey('');
      setGeminiKey('');
      setDeepseekKey('');
    },
    onError: () => toast.error('Unable to save integrations'),
  });

  const handleSave = (e: FormEvent) => {
    e.preventDefault();
    save.mutate({
      vapi: { api_key: vapiApiKey, voice_id: vapiVoiceId, phone_number_id: vapiPhoneId },
      leads: {
        google_places_api_key: googlePlaces,
        adzuna_app_id: adzunaAppId,
        adzuna_app_key: adzunaAppKey,
        adzuna_country: adzunaCountry,
      },
      llm: {
        openai_api_key: openaiKey,
        gemini_api_key: geminiKey,
        deepseek_api_key: deepseekKey,
      },
    });
  };

  return (
    <div className="space-y-3">
      {/* Status summary */}
      <div className="bg-display-black border border-digital-white/10 rounded-lg p-4">
        <h2 className={sectionTitle}>Configured Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {configuredSummary.map(([label, ok]) => (
            <div
              key={label}
              className="flex items-center justify-between border border-digital-white/[0.08] rounded px-3 py-2"
            >
              <span className="text-[12px] text-slate-blue">{label}</span>
              <span
                className={`text-[11px] font-sf-mono uppercase tracking-[0.04em] ${
                  ok ? 'text-digital-white' : 'text-steel-grey'
                }`}
              >
                {ok ? 'Configured' : 'Not set'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Update form */}
      <form
        className="bg-display-black border border-digital-white/10 rounded-lg p-4 space-y-4"
        onSubmit={handleSave}
      >
        <h2 className={sectionTitle}>Update Integrations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input label="VAPI API key" type="password" value={vapiApiKey} onChange={(e) => setVapiApiKey(e.target.value)} />
          <Input label="VAPI Voice ID" value={vapiVoiceId} onChange={(e) => setVapiVoiceId(e.target.value)} />
          <Input label="VAPI Phone Number ID" value={vapiPhoneId} onChange={(e) => setVapiPhoneId(e.target.value)} />
          <Input label="Google Places API key" type="password" value={googlePlaces} onChange={(e) => setGooglePlaces(e.target.value)} />
          <Input label="Adzuna App ID" type="password" value={adzunaAppId} onChange={(e) => setAdzunaAppId(e.target.value)} />
          <Input label="Adzuna App Key" type="password" value={adzunaAppKey} onChange={(e) => setAdzunaAppKey(e.target.value)} />
          <Input label="Adzuna Country" value={adzunaCountry} onChange={(e) => setAdzunaCountry(e.target.value)} />
          <Input label="OpenAI API key" type="password" value={openaiKey} onChange={(e) => setOpenaiKey(e.target.value)} />
          <Input label="Gemini API key" type="password" value={geminiKey} onChange={(e) => setGeminiKey(e.target.value)} />
          <Input label="Deepseek API key" type="password" value={deepseekKey} onChange={(e) => setDeepseekKey(e.target.value)} />
        </div>
        <Button type="submit" loading={save.isPending}>
          Save Integrations
        </Button>
      </form>
    </div>
  );
}
