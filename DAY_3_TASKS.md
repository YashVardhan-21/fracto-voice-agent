# DAY 3: Frontend Dashboard + Deployment
## 8-10 Hour Sprint - SHIP IT! 🚀

---

## 🌅 MORNING SESSION (4 hours) - 8:00 AM - 12:00 PM

### Task 3.1: Frontend Setup (1 hour) ⏰ 8:00-9:00 AM

```bash
# Navigate to frontend directory
cd frontend

# Initialize React with Vite
npm create vite@latest . -- --template react
npm install

# Install dependencies
npm install axios @tanstack/react-query react-router-dom
npm install lucide-react clsx tailwind-merge
npm install recharts

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui components
npx shadcn-ui@latest init
```

**Update tailwind.config.js:**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

**Update src/index.css:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

**Create API client: src/services/api.js**

```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const jobsApi = {
  scrapeJobs: (data) => api.post('/api/scrape-jobs', data),
  getJobs: (params) => api.get('/api/jobs', { params }),
};

export const companiesApi = {
  analyzeWebsite: (data) => api.post('/api/analyze-website', data),
  getCompanies: (params) => api.get('/api/companies', { params }),
};

export const voiceAgentsApi = {
  createAgent: (data) => api.post('/api/create-voice-agent', data),
  getAgents: (params) => api.get('/api/voice-agents', { params }),
};

export const campaignsApi = {
  processCampaign: (data) => api.post('/api/process-campaign', data),
  processCampaignAsync: (data) => api.post('/api/process-campaign-async', data),
  getTaskStatus: (taskId) => api.get(`/api/task-status/${taskId}`),
};

export default api;
```

**Create .env file:**

```env
VITE_API_URL=http://localhost:8000
```

**Checkpoint:** ✅ Frontend project initialized with all dependencies

---

### Task 3.2: Layout & Navigation (1 hour) ⏰ 9:00-10:00 AM

**Create layout: src/components/Layout.jsx**

```jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Phone, Users, TrendingUp, Settings, Zap } from 'lucide-react';

export default function Layout({ children }) {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: TrendingUp },
    { name: 'Campaigns', href: '/campaigns', icon: Zap },
    { name: 'Companies', href: '/companies', icon: Users },
    { name: 'Voice Agents', href: '/agents', icon: Phone },
  ];
  
  const isActive = (href) => {
    return location.pathname === href;
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Phone className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                FRACTO Voice Agent
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Admin User</span>
            </div>
          </div>
        </div>
      </header>
      
      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 bg-white h-[calc(100vh-64px)] border-r border-gray-200 p-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={`flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                      active
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className={`mr-3 h-5 w-5 ${active ? 'text-blue-700' : 'text-gray-400'}`} />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        
        {/* Main Content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
```

**Checkpoint:** ✅ Layout with sidebar navigation created

---

### Task 3.3: Dashboard Page (1 hour) ⏰ 10:00-11:00 AM

**Create dashboard: src/pages/Dashboard.jsx**

```jsx
import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { jobsApi, companiesApi, voiceAgentsApi } from '../services/api';
import { TrendingUp, Users, Phone, Zap } from 'lucide-react';

function StatCard({ title, value, icon: Icon, color = 'blue' }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 bg-${color}-50 rounded-lg`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { data: jobs = [] } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.getJobs().then(res => res.data),
  });
  
  const { data: companies = [] } = useQuery({
    queryKey: ['companies'],
    queryFn: () => companiesApi.getCompanies().then(res => res.data),
  });
  
  const { data: agents = [] } = useQuery({
    queryKey: ['agents'],
    queryFn: () => voiceAgentsApi.getAgents().then(res => res.data),
  });
  
  const avgConfidence = companies.length > 0
    ? (companies.reduce((sum, c) => sum + (c.confidence_score || 0), 0) / companies.length * 100).toFixed(1)
    : 0;
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your voice agent automation</p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Jobs Scraped"
          value={jobs.length}
          icon={TrendingUp}
          color="blue"
        />
        <StatCard
          title="Companies Analyzed"
          value={companies.length}
          icon={Users}
          color="green"
        />
        <StatCard
          title="Voice Agents Created"
          value={agents.length}
          icon={Phone}
          color="purple"
        />
        <StatCard
          title="Avg Confidence Score"
          value={`${avgConfidence}%`}
          icon={Zap}
          color="orange"
        />
      </div>
      
      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Voice Agents</h2>
        </div>
        <div className="p-6">
          {agents.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No voice agents created yet. Start a new campaign!
            </p>
          ) : (
            <div className="space-y-4">
              {agents.slice(0, 5).map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <Phone className="h-5 w-5 text-blue-600 mr-3" />
                    <div>
                      <p className="font-medium text-gray-900">{agent.name}</p>
                      <p className="text-sm text-gray-500">VAPI ID: {agent.vapi_assistant_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      agent.status === 'created' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Checkpoint:** ✅ Dashboard showing stats and recent agents

---

### Task 3.4: Campaign Creation Page (1 hour) ⏰ 11:00 AM - 12:00 PM

**Create campaigns page: src/pages/Campaigns.jsx**

```jsx
import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { campaignsApi } from '../services/api';
import { Play, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';

export default function Campaigns() {
  const [formData, setFormData] = useState({
    campaign_name: '',
    job_query: '',
    location: '',
    limit: 5,
  });
  
  const [taskId, setTaskId] = useState(null);
  const [pollCount, setPollCount] = useState(0);
  
  // Mutation for starting campaign
  const startCampaign = useMutation({
    mutationFn: (data) => campaignsApi.processCampaignAsync(data).then(res => res.data),
    onSuccess: (data) => {
      setTaskId(data.task_id);
      setPollCount(0);
    },
  });
  
  // Query for polling task status
  const { data: taskStatus } = useQuery({
    queryKey: ['taskStatus', taskId],
    queryFn: () => campaignsApi.getTaskStatus(taskId).then(res => res.data),
    enabled: !!taskId && pollCount < 60,
    refetchInterval: (data) => {
      if (!data) return 3000;
      const status = data.status;
      if (status === 'completed' || status === 'failed') return false;
      setPollCount(prev => prev + 1);
      return 3000;
    },
  });
  
  const handleSubmit = (e) => {
    e.preventDefault();
    startCampaign.mutate(formData);
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'limit' ? parseInt(value) : value,
    }));
  };
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-600 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Campaign</h1>
        <p className="text-gray-600 mt-1">Automate voice agent creation for job postings</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Campaign Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Campaign Settings</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Campaign Name
              </label>
              <input
                type="text"
                name="campaign_name"
                value={formData.campaign_name}
                onChange={handleChange}
                required
                placeholder="e.g., Dental Offices NYC"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Search Query
              </label>
              <input
                type="text"
                name="job_query"
                value={formData.job_query}
                onChange={handleChange}
                required
                placeholder="e.g., dental office manager"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., New York, NY"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Jobs to Process
              </label>
              <input
                type="number"
                name="limit"
                value={formData.limit}
                onChange={handleChange}
                min="1"
                max="50"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Start with 5-10 for testing</p>
            </div>
            
            <button
              type="submit"
              disabled={startCampaign.isPending}
              className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {startCampaign.isPending ? (
                <>
                  <Loader className="animate-spin h-5 w-5 mr-2" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5 mr-2" />
                  Start Campaign
                </>
              )}
            </button>
          </form>
        </div>
        
        {/* Campaign Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Campaign Status</h2>
          
          {!taskId ? (
            <div className="text-center py-12 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p>No active campaign</p>
              <p className="text-sm mt-1">Start a campaign to see progress</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Task ID</span>
                <span className="text-sm text-gray-900 font-mono">{taskId.slice(0, 8)}...</span>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Status</span>
                <div className="flex items-center">
                  {getStatusIcon(taskStatus?.status)}
                  <span className="ml-2 text-sm font-medium capitalize">
                    {taskStatus?.status || 'pending'}
                  </span>
                </div>
              </div>
              
              {taskStatus?.status === 'completed' && taskStatus?.result && (
                <div className="space-y-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex justify-between">
                    <span className="text-sm text-green-800">Jobs Processed:</span>
                    <span className="text-sm font-bold text-green-900">
                      {taskStatus.result.jobs_processed}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-green-800">Agents Created:</span>
                    <span className="text-sm font-bold text-green-900">
                      {taskStatus.result.agents_created}
                    </span>
                  </div>
                  {taskStatus.result.errors && taskStatus.result.errors.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-green-200">
                      <p className="text-sm text-red-600 font-medium">Errors:</p>
                      <ul className="text-xs text-red-600 mt-1 space-y-1">
                        {taskStatus.result.errors.slice(0, 3).map((error, i) => (
                          <li key={i}>• {error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              {taskStatus?.status === 'failed' && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800 font-medium">Campaign Failed</p>
                  <p className="text-xs text-red-600 mt-1">{taskStatus?.error}</p>
                </div>
              )}
              
              {taskStatus?.status === 'processing' && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center">
                    <Loader className="animate-spin h-5 w-5 text-blue-600 mr-2" />
                    <span className="text-sm text-blue-800">
                      Processing campaign... This may take several minutes.
                    </span>
                  </div>
                  <p className="text-xs text-blue-600 mt-2">
                    Poll count: {pollCount}/60
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Checkpoint:** ✅ Campaign creation page with real-time status updates

---

## ☀️ AFTERNOON SESSION (4 hours) - 2:00 PM - 6:00 PM

### Task 3.5: Companies & Agents Pages (1.5 hours) ⏰ 2:00-3:30 PM

**Create companies page: src/pages/Companies.jsx**

```jsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { companiesApi } from '../services/api';
import { Building2, Globe, Phone, Mail, TrendingUp } from 'lucide-react';

export default function Companies() {
  const { data: companies = [], isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: () => companiesApi.getCompanies().then(res => res.data),
  });
  
  const getBusinessTypeColor = (type) => {
    const colors = {
      dental: 'bg-blue-100 text-blue-800',
      medical: 'bg-green-100 text-green-800',
      legal: 'bg-purple-100 text-purple-800',
      default: 'bg-gray-100 text-gray-800',
    };
    return colors[type] || colors.default;
  };
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analyzed Companies</h1>
        <p className="text-gray-600 mt-1">Companies extracted from job postings</p>
      </div>
      
      {companies.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Building2 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">No companies analyzed yet</p>
          <p className="text-sm text-gray-400 mt-1">Start a campaign to see results</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {companies.map((company) => (
            <div key={company.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <Building2 className="h-5 w-5 text-gray-400 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getBusinessTypeColor(company.business_type)}`}>
                    {company.business_type}
                  </span>
                </div>
                
                <div className="space-y-2">
                  {company.website && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Globe className="h-4 w-4 mr-2" />
                      <a href={company.website} target="_blank" rel="noopener noreferrer" 
                         className="text-blue-600 hover:underline">
                        {company.website}
                      </a>
                    </div>
                  )}
                  
                  {company.contact_phone && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Phone className="h-4 w-4 mr-2" />
                      {company.contact_phone}
                    </div>
                  )}
                  
                  {company.contact_email && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Mail className="h-4 w-4 mr-2" />
                      {company.contact_email}
                    </div>
                  )}
                  
                  {company.services && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-medium text-gray-500 mb-1">Services:</p>
                      <p className="text-sm text-gray-700">{company.services}</p>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center text-xs text-gray-500">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      Confidence: {(company.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Create voice agents page: src/pages/VoiceAgents.jsx**

```jsx
import React, { useState } from 'react';
import { useQuery } from '@tantml:react-query';
import { voiceAgentsApi } from '../services/api';
import { Phone, Copy, CheckCircle } from 'lucide-react';

export default function VoiceAgents() {
  const [copiedId, setCopiedId] = useState(null);
  
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => voiceAgentsApi.getAgents().then(res => res.data),
  });
  
  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Voice Agents</h1>
        <p className="text-gray-600 mt-1">VAPI voice assistants created for each company</p>
      </div>
      
      {agents.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Phone className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">No voice agents created yet</p>
          <p className="text-sm text-gray-400 mt-1">Start a campaign to create agents</p>
        </div>
      ) : (
        <div className="space-y-4">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <Phone className="h-6 w-6 text-blue-600 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <div className="flex items-center mt-1">
                        <span className="text-sm text-gray-500 font-mono mr-2">
                          {agent.vapi_assistant_id}
                        </span>
                        <button
                          onClick={() => copyToClipboard(agent.vapi_assistant_id, agent.id)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          {copiedId === agent.id ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                  <span className={`px-3 py-1 text-sm font-medium rounded ${
                    agent.status === 'created' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {agent.status}
                  </span>
                </div>
                
                <div className="bg-gray-50 rounded p-4">
                  <p className="text-xs font-medium text-gray-500 mb-2">System Prompt:</p>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-4">
                    {agent.prompt}
                  </p>
                </div>
                
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-500">
                    Voice: <span className="font-medium text-gray-700">{agent.voice_type}</span>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700">
                    Test Agent
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Checkpoint:** ✅ Companies and Voice Agents pages complete

---

### Task 3.6: Routing & App Setup (30 min) ⏰ 3:30-4:00 PM

**Update src/App.jsx:**

```jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Campaigns from './pages/Campaigns';
import Companies from './pages/Companies';
import VoiceAgents from './pages/VoiceAgents';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/agents" element={<VoiceAgents />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

**Update src/main.jsx:**

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**Test the frontend:**

```bash
npm run dev
# Open browser: http://localhost:5173
```

**Checkpoint:** ✅ Full frontend working with all pages

---

### Task 3.7: Docker & Deployment (2.5 hours) ⏰ 4:00-6:30 PM

**Update backend/Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Update frontend/Dockerfile:**

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Create frontend/nginx.conf:**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Update docker-compose.yml:**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./fracto.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - VAPI_API_KEY=${VAPI_API_KEY}
      - SCRAPER_API_KEY=${SCRAPER_API_KEY}
    volumes:
      - ./backend:/app
      - backend_data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000
    restart: unless-stopped

volumes:
  backend_data:
```

**Create .env file in root:**

```env
OPENAI_API_KEY=your_openai_key
VAPI_API_KEY=your_vapi_key
SCRAPER_API_KEY=your_scraper_key
```

**Build and run with Docker:**

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Deploy to Railway (easiest):**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variables in Railway dashboard
```

**Checkpoint:** ✅ Docker setup complete, ready to deploy

---

## 🌙 EVENING WRAP-UP (1.5 hours) - 6:30-8:00 PM

### Task 3.8: Final Testing & Documentation (1.5 hours)

**Create comprehensive README:**

```bash
cat > README.md << 'EOF'
# FRACTO Voice Agent Outreach Automation

🚀 **AI-powered voice agent creation system that automates outreach campaigns**

## Features

- ✅ Job scraping from Indeed
- ✅ Automated website analysis with GPT-4
- ✅ Industry-specific prompt generation
- ✅ VAPI voice agent creation
- ✅ Real-time campaign monitoring
- ✅ Beautiful React dashboard

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker (optional)
- API Keys: OpenAI, VAPI

### Local Development

**Backend:**
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app.main:app --reload
\`\`\`

**Frontend:**
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

### Docker Deployment

\`\`\`bash
docker-compose up -d
\`\`\`

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Create Campaign**: Go to Campaigns page
2. **Enter Job Query**: e.g., "dental office manager"
3. **Set Location**: e.g., "New York, NY"
4. **Start**: Click "Start Campaign"
5. **Monitor**: Watch real-time progress
6. **Results**: View created voice agents

## API Endpoints

- `POST /api/scrape-jobs` - Scrape job listings
- `POST /api/analyze-website` - Analyze company website
- `POST /api/create-voice-agent` - Create VAPI assistant
- `POST /api/process-campaign-async` - Full campaign workflow
- `GET /api/task-status/{task_id}` - Check campaign status

## Architecture

\`\`\`
Frontend (React + Vite) → Backend (FastAPI) → APIs (OpenAI, VAPI)
                                ↓
                           SQLite Database
\`\`\`

## Cost Estimates

- OpenAI GPT-4o-mini: ~$0.50 per 100 analyses
- VAPI: ~$0.10 per minute of voice calls
- ScraperAPI: $49/month (optional, fallback to mock data)

**Total MVP cost: ~$20-50/month**

## Roadmap

- [x] MVP: Core workflow (3 days)
- [ ] LinkedIn scraping integration
- [ ] Email outreach automation
- [ ] Advanced analytics dashboard
- [ ] Multi-user support
- [ ] White-label solution

## Contributing

Built with ❤️ by FRACTO team

## License

MIT
EOF
```

**Final testing checklist:**

```markdown
# Final Testing Checklist

## Backend
- [ ] API starts without errors
- [ ] Swagger docs accessible
- [ ] Can scrape jobs (mock data OK)
- [ ] Website analysis works
- [ ] Voice agent creation works
- [ ] Background tasks work
- [ ] Database persists data

## Frontend
- [ ] All pages load
- [ ] Navigation works
- [ ] Dashboard shows stats
- [ ] Campaign creation works
- [ ] Real-time status updates
- [ ] Companies list displays
- [ ] Voice agents list displays

## Integration
- [ ] Frontend connects to backend
- [ ] API calls succeed
- [ ] Error handling works
- [ ] Loading states work

## Deployment
- [ ] Docker builds successfully
- [ ] Docker compose runs
- [ ] Environment variables work
- [ ] Data persists in volumes

## Demo
- [ ] Can create campaign in <3 minutes
- [ ] Voice agent created successfully
- [ ] Dashboard shows results
- [ ] System is responsive
```

**Create demo script:**

```markdown
# 5-Minute Demo Script

## Setup (30 seconds)
1. Open http://localhost:3000
2. Show dashboard (currently empty)

## Create Campaign (2 minutes)
1. Click "Campaigns" in sidebar
2. Fill form:
   - Name: "Dental Offices NYC Demo"
   - Query: "dental office manager"
   - Location: "New York"
   - Limit: 3
3. Click "Start Campaign"
4. Show real-time status updates

## Show Results (2 minutes)
1. Wait for "Completed" status
2. Click "Dashboard" - show updated stats
3. Click "Companies" - show analyzed companies
4. Click "Voice Agents" - show created agents
5. Click "Test Agent" - demo voice agent (if VAPI configured)

## Highlight Value (30 seconds)
- "From 2 hours manual work to 2 minutes automation"
- "Personalized voice agents for each business"
- "90% time savings, 70% better conversion"
```

---

## 🎯 DAY 3 SUCCESS CRITERIA

**Must Be Completed:**
- ✅ Frontend fully functional
- ✅ All pages working (Dashboard, Campaigns, Companies, Agents)
- ✅ Real-time campaign monitoring
- ✅ Docker setup complete
- ✅ README documentation
- ✅ Demo-ready system

**Stretch Goals:**
- ⭐ Deployed to cloud (Railway/Render)
- ⭐ Demo video recorded
- ⭐ Advanced error handling
- ⭐ Export functionality

---

## 🎉 PROJECT COMPLETE!

**What You've Built:**
- ✅ Full-stack voice agent automation system
- ✅ Job scraping + website analysis
- ✅ AI-powered prompt generation
- ✅ VAPI integration
- ✅ Beautiful React dashboard
- ✅ Docker deployment

**Next Steps:**
1. Test with real API keys
2. Create demo video
3. Deploy to cloud
4. Show to stakeholders
5. Gather feedback
6. Plan next features

**Congratulations! 🚀 You've built an enterprise-grade AI automation system in 3 days!**

