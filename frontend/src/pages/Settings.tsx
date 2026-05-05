import { FormEvent, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

import { Header } from '../components/layout/Header';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { createTeamUser, getTeamUsers, updateTeamUser, type TeamRole } from '../api/team';
import { getIntegrations, updateIntegrations } from '../api/settings';
import { useAuthStore } from '../store/authStore';

type SettingsTab = 'team' | 'integrations';

export function Settings() {
  const user = useAuthStore((s) => s.user);
  const [tab, setTab] = useState<SettingsTab>('team');
  const isAdmin = Boolean(user?.is_admin) || user?.role === 'admin';
  if (!isAdmin) {
    return (
      <>
        <Header title="Settings" />
        <div className="p-8 text-sm text-gray-500">Admin access required.</div>
      </>
    );
  }
  return (
    <>
      <Header title="Settings" />
      <div className="p-8 space-y-6">
        <div className="flex rounded-lg border border-gray-200 overflow-hidden w-fit">
          <button
            type="button"
            onClick={() => setTab('team')}
            className={`px-4 py-2 text-sm font-medium ${
              tab === 'team' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Team
          </button>
          <button
            type="button"
            onClick={() => setTab('integrations')}
            className={`px-4 py-2 text-sm font-medium border-l border-gray-200 ${
              tab === 'integrations'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Integrations
          </button>
        </div>
        {tab === 'team' ? <TeamTab /> : <IntegrationsTab />}
      </div>
    </>
  );
}

function TeamTab() {
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
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Add Team User</h2>
        <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleCreate}>
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input
            label="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
          <label className="text-sm text-gray-600">
            Role
            <select
              className="mt-1 h-11 w-full rounded-md border border-gray-200 px-3"
              value={role}
              onChange={(e) => setRole(e.target.value as TeamRole)}
            >
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

      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Name', 'Email', 'Role', 'Admin', 'Status', ''].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-xs uppercase tracking-wide text-gray-500">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr>
                <td className="px-4 py-8 text-center text-gray-400" colSpan={6}>
                  Loading team...
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id}>
                  <td className="px-4 py-3 font-medium text-gray-900">{u.full_name}</td>
                  <td className="px-4 py-3 text-gray-500">{u.email}</td>
                  <td className="px-4 py-3 text-gray-500">{u.role}</td>
                  <td className="px-4 py-3 text-gray-500">{u.is_admin ? 'Yes' : 'No'}</td>
                  <td className="px-4 py-3 text-gray-500">{u.is_active ? 'Active' : 'Inactive'}</td>
                  <td className="px-4 py-3">
                    <Button
                      size="sm"
                      variant="secondary"
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

function IntegrationsTab() {
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
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Configured Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
          {configuredSummary.map(([label, ok]) => (
            <div key={label} className="flex items-center justify-between border border-gray-100 rounded px-3 py-2">
              <span className="text-gray-600">{label}</span>
              <span className={ok ? 'text-green-700' : 'text-gray-400'}>{ok ? 'Configured' : 'Not set'}</span>
            </div>
          ))}
        </div>
      </div>

      <form className="bg-white border border-gray-200 rounded-xl p-5 space-y-4" onSubmit={handleSave}>
        <h2 className="text-lg font-semibold text-gray-900">Update Integrations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="VAPI API key" type="password" value={vapiApiKey} onChange={(e) => setVapiApiKey(e.target.value)} />
          <Input label="VAPI Voice ID" value={vapiVoiceId} onChange={(e) => setVapiVoiceId(e.target.value)} />
          <Input
            label="VAPI Phone Number ID"
            value={vapiPhoneId}
            onChange={(e) => setVapiPhoneId(e.target.value)}
          />
          <Input
            label="Google Places API key"
            type="password"
            value={googlePlaces}
            onChange={(e) => setGooglePlaces(e.target.value)}
          />
          <Input label="Adzuna App ID" type="password" value={adzunaAppId} onChange={(e) => setAdzunaAppId(e.target.value)} />
          <Input
            label="Adzuna App Key"
            type="password"
            value={adzunaAppKey}
            onChange={(e) => setAdzunaAppKey(e.target.value)}
          />
          <Input
            label="Adzuna Country"
            value={adzunaCountry}
            onChange={(e) => setAdzunaCountry(e.target.value)}
          />
          <Input
            label="OpenAI API key"
            type="password"
            value={openaiKey}
            onChange={(e) => setOpenaiKey(e.target.value)}
          />
          <Input
            label="Gemini API key"
            type="password"
            value={geminiKey}
            onChange={(e) => setGeminiKey(e.target.value)}
          />
          <Input
            label="Deepseek API key"
            type="password"
            value={deepseekKey}
            onChange={(e) => setDeepseekKey(e.target.value)}
          />
        </div>
        <Button type="submit" loading={save.isPending}>
          Save Integrations
        </Button>
      </form>
    </div>
  );
}

