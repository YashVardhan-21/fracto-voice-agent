import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { login } from '../api/auth';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import toast from 'react-hot-toast';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await login(email, password);
      setAuth(data.access_token, {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        role: data.role as 'agent' | 'manager' | 'admin',
        is_admin: data.is_admin,
        tenant_id: data.tenant_id,
      });
      navigate('/');
    } catch {
      toast.error('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-display-black flex items-center justify-center p-4">
      <div className="bg-display-black border border-digital-white/20 rounded-cards shadow-subtle-2 p-8 w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="text-2xl text-urgency-red font-sf-mono">●</span>
          <h1 className="text-2xl font-semibold text-digital-white mt-2 tracking-[0.08em] uppercase font-sf-mono">
            FRACTO
          </h1>
          <p className="text-slate-blue text-xs uppercase tracking-[0.05em] mt-2">Voice Agent Platform</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
            placeholder="agent@mission.local"
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
          />
          <Button type="submit" loading={loading} className="w-full justify-center">
            Sign in
          </Button>
        </form>
      </div>
    </div>
  );
}
