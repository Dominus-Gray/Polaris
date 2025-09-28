import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  return (
    <div className="container mt-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Administration Dashboard</h1>
        <p className="text-slate-600 mt-1">Manage users, monitor system health, and configure platform settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1">
          <nav className="bg-white rounded-lg shadow-sm border p-4 sticky top-6">
            <div className="space-y-1">
              <AdminNavItem 
                icon="📊" 
                label="Overview" 
                id="overview"
                active={activeTab === 'overview'}
                onClick={() => setActiveTab('overview')}
              />
              <AdminNavItem 
                icon="👥" 
                label="User Management" 
                id="users"
                active={activeTab === 'users'}
                onClick={() => setActiveTab('users')}
              />
              <AdminNavItem 
                icon="🔐" 
                label="Roles & Permissions" 
                id="roles"
                active={activeTab === 'roles'}
                onClick={() => setActiveTab('roles')}
              />
              <AdminNavItem 
                icon="📋" 
                label="Audit Logs" 
                id="audit"
                active={activeTab === 'audit'}
                onClick={() => setActiveTab('audit')}
              />
              <AdminNavItem 
                icon="🚀" 
                label="Feature Flags" 
                id="features"
                active={activeTab === 'features'}
                onClick={() => setActiveTab('features')}
              />
              <AdminNavItem 
                icon="🏢" 
                label="Business Profiles" 
                id="businesses"
                active={activeTab === 'businesses'}
                onClick={() => setActiveTab('businesses')}
              />
              <AdminNavItem 
                icon="🎯" 
                label="Assessments" 
                id="assessments"
                active={activeTab === 'assessments'}
                onClick={() => setActiveTab('assessments')}
              />
              <AdminNavItem 
                icon="📜" 
                label="Certificates" 
                id="certificates"
                active={activeTab === 'certificates'}
                onClick={() => setActiveTab('certificates')}
              />
              <AdminNavItem 
                icon="⚙️" 
                label="System Config" 
                id="config"
                active={activeTab === 'config'}
                onClick={() => setActiveTab('config')}
              />
              <AdminNavItem 
                icon="💾" 
                label="Data Governance" 
                id="data"
                active={activeTab === 'data'}
                onClick={() => setActiveTab('data')}
              />
            </div>
          </nav>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-4">
          <div className="space-y-6">
            {activeTab === 'overview' && <OverviewTab />}
            {activeTab === 'users' && <UserManagementTab />}
            {activeTab === 'roles' && <RolesPermissionsTab />}
            {activeTab === 'audit' && <AuditLogsTab />}
            {activeTab === 'features' && <FeatureFlagsTab />}
            {activeTab === 'businesses' && <BusinessProfilesTab />}
            {activeTab === 'assessments' && <AssessmentsTab />}
            {activeTab === 'certificates' && <CertificatesTab />}
            {activeTab === 'config' && <SystemConfigTab />}
            {activeTab === 'data' && <DataGovernanceTab />}
          </div>
        </div>
      </div>
    </div>
  );
}

function AdminNavItem({ icon, label, id, active, onClick }) {
  return (
    <button
      className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg transition-colors text-sm ${
        active 
          ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-500 font-medium' 
          : 'hover:bg-slate-50 text-slate-700'
      }`}
      onClick={onClick}
    >
      <span className="text-lg">{icon}</span>
      <span>{label}</span>
    </button>
  );
}

function OverviewTab() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSystemStats();
  }, []);

  const loadSystemStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/system/stats`);
      setStats(response.data);
    } catch (error) {
      toast.error('Failed to load system statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-center">Loading system overview...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Users"
          value={stats?.total_users || 0}
          change="+12%"
          trend="up"
          icon="👥"
        />
        <MetricCard
          title="Active Businesses"
          value={stats?.active_businesses || 0}
          change="+8%"
          trend="up"
          icon="🏢"
        />
        <MetricCard
          title="Certificates Issued"
          value={stats?.certificates_issued || 0}
          change="+24%"
          trend="up"
          icon="📜"
        />
        <MetricCard
          title="System Health"
          value="99.9%"
          change="Stable"
          trend="stable"
          icon="💚"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent User Registrations</h3>
          <div className="space-y-3">
            {stats?.recent_users?.map(user => (
              <div key={user.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-b-0">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center">
                    {user.name?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div>
                    <div className="font-medium text-slate-900">{user.name}</div>
                    <div className="text-sm text-slate-600">{user.email}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-slate-600">{user.role}</div>
                  <div className="text-xs text-slate-500">{new Date(user.created_at).toLocaleDateString()}</div>
                </div>
              </div>
            )) || (
              <div className="text-center py-8 text-slate-500">No recent registrations</div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">System Alerts</h3>
          <div className="space-y-3">
            <SystemAlert
              type="info"
              title="Scheduled Maintenance"
              message="System maintenance scheduled for this weekend"
              timestamp="2 hours ago"
            />
            <SystemAlert
              type="warning"
              title="High API Usage"
              message="OAuth API calls approaching rate limit"
              timestamp="5 hours ago"
            />
            <SystemAlert
              type="success"
              title="Backup Completed"
              message="Daily database backup completed successfully"
              timestamp="8 hours ago"
            />
          </div>
        </div>
      </div>

      {/* Platform Health */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Platform Health Monitor</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <HealthMetric
            label="API Response Time"
            value="145ms"
            status="good"
            target="< 200ms"
          />
          <HealthMetric
            label="Database Connections"
            value="23/100"
            status="good"
            target="< 80"
          />
          <HealthMetric
            label="Storage Usage"
            value="67%"
            status="warning"
            target="< 80%"
          />
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, change, trend, icon }) {
  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-slate-600';

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium text-slate-600">{title}</div>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="text-2xl font-bold text-slate-900 mb-1">{value}</div>
      <div className={`text-sm ${trendColor}`}>{change}</div>
    </div>
  );
}

function SystemAlert({ type, title, message, timestamp }) {
  const colors = {
    info: 'border-blue-200 bg-blue-50 text-blue-800',
    warning: 'border-yellow-200 bg-yellow-50 text-yellow-800',
    success: 'border-green-200 bg-green-50 text-green-800',
    error: 'border-red-200 bg-red-50 text-red-800'
  };

  return (
    <div className={`border rounded-lg p-3 ${colors[type]}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="font-medium">{title}</div>
          <div className="text-sm mt-1">{message}</div>
        </div>
        <div className="text-xs">{timestamp}</div>
      </div>
    </div>
  );
}

function HealthMetric({ label, value, status, target }) {
  const statusColor = status === 'good' ? 'text-green-600' : status === 'warning' ? 'text-yellow-600' : 'text-red-600';
  const statusBg = status === 'good' ? 'bg-green-100' : status === 'warning' ? 'bg-yellow-100' : 'bg-red-100';

  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <div className="font-medium text-slate-900">{label}</div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${statusBg} ${statusColor}`}>
          {status}
        </div>
      </div>
      <div className="text-xl font-bold text-slate-900">{value}</div>
      <div className="text-sm text-slate-600">Target: {target}</div>
    </div>
  );
}

function UserManagementTab() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    role: '',
    status: '',
    search: ''
  });
  const [selectedUsers, setSelectedUsers] = useState([]);

  useEffect(() => {
    loadUsers();
  }, [filters]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await axios.get(`${API}/admin/users?${params}`);
      setUsers(response.data.users || []);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkAction = async (action) => {
    if (selectedUsers.length === 0) {
      toast.error('Please select users first');
      return;
    }

    try {
      await axios.post(`${API}/admin/users/bulk-action`, {
        action,
        user_ids: selectedUsers
      });
      
      toast.success(`${action} completed for ${selectedUsers.length} users`);
      setSelectedUsers([]);
      loadUsers();
    } catch (error) {
      toast.error(`Failed to ${action} users`);
    }
  };

  const handleUserAction = async (userId, action) => {
    try {
      await axios.post(`${API}/admin/users/${userId}/action`, { action });
      toast.success(`User ${action} successfully`);
      loadUsers();
    } catch (error) {
      toast.error(`Failed to ${action} user`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-slate-900">User Management</h2>
          <button className="btn btn-primary">
            + Invite User
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-64">
            <input
              type="text"
              placeholder="Search by name or email..."
              className="input w-full"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>
          <select
            className="input"
            value={filters.role}
            onChange={(e) => setFilters({ ...filters, role: e.target.value })}
          >
            <option value="">All Roles</option>
            <option value="client">Client</option>
            <option value="provider">Provider</option>
            <option value="navigator">Navigator</option>
            <option value="agency">Agency</option>
            <option value="admin">Admin</option>
          </select>
          <select
            className="input"
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>

        {/* Bulk Actions */}
        {selectedUsers.length > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-800">
                {selectedUsers.length} users selected
              </span>
              <div className="flex gap-2">
                <button
                  className="btn btn-sm"
                  onClick={() => handleBulkAction('activate')}
                >
                  Activate
                </button>
                <button
                  className="btn btn-sm"
                  onClick={() => handleBulkAction('deactivate')}
                >
                  Deactivate
                </button>
                <button
                  className="btn btn-sm bg-red-600 text-white"
                  onClick={() => handleBulkAction('suspend')}
                >
                  Suspend
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left py-3 px-4">
                <input
                  type="checkbox"
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedUsers(users.map(u => u.id));
                    } else {
                      setSelectedUsers([]);
                    }
                  }}
                />
              </th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">User</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Role</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Status</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Created</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Last Active</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="7" className="text-center py-8">Loading users...</td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center py-8 text-slate-500">No users found</td>
              </tr>
            ) : users.map(user => (
              <tr key={user.id} className="border-t hover:bg-slate-50">
                <td className="py-3 px-4">
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(user.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedUsers([...selectedUsers, user.id]);
                      } else {
                        setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                      }
                    }}
                  />
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center">
                      {user.name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-slate-900">{user.name || 'No name'}</div>
                      <div className="text-sm text-slate-600">{user.email}</div>
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                    {user.role}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                    {user.status}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-slate-600">
                  {new Date(user.created_at).toLocaleDateString()}
                </td>
                <td className="py-3 px-4 text-sm text-slate-600">
                  {user.last_sign_in ? new Date(user.last_sign_in).toLocaleDateString() : 'Never'}
                </td>
                <td className="py-3 px-4">
                  <div className="flex gap-2">
                    <button
                      className="text-blue-600 hover:text-blue-700 text-sm"
                      onClick={() => handleUserAction(user.id, 'edit')}
                    >
                      Edit
                    </button>
                    <button
                      className="text-red-600 hover:text-red-700 text-sm"
                      onClick={() => handleUserAction(user.id, user.status === 'active' ? 'suspend' : 'activate')}
                    >
                      {user.status === 'active' ? 'Suspend' : 'Activate'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getRoleColor(role) {
  const colors = {
    'admin': 'bg-purple-100 text-purple-800',
    'navigator': 'bg-blue-100 text-blue-800',
    'agency': 'bg-green-100 text-green-800',
    'provider': 'bg-orange-100 text-orange-800',
    'client': 'bg-slate-100 text-slate-800'
  };
  return colors[role] || 'bg-slate-100 text-slate-800';
}

function getStatusColor(status) {
  const colors = {
    'active': 'bg-green-100 text-green-800',
    'inactive': 'bg-slate-100 text-slate-800',
    'suspended': 'bg-red-100 text-red-800'
  };
  return colors[status] || 'bg-slate-100 text-slate-800';
}

function AuditLogsTab() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    resource: '',
    date_from: '',
    date_to: ''
  });

  useEffect(() => {
    loadAuditLogs();
  }, [filters]);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await axios.get(`${API}/admin/audit-logs?${params}`);
      setLogs(response.data.logs || []);
    } catch (error) {
      toast.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 border-b">
        <h2 className="text-xl font-semibold text-slate-900 mb-4">Audit Logs</h2>
        
        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <input
            type="text"
            placeholder="User ID"
            className="input"
            value={filters.user_id}
            onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
          />
          <select
            className="input"
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value })}
          >
            <option value="">All Actions</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
            <option value="profile_update">Profile Update</option>
            <option value="certificate_issued">Certificate Issued</option>
            <option value="assessment_completed">Assessment Completed</option>
          </select>
          <select
            className="input"
            value={filters.resource}
            onChange={(e) => setFilters({ ...filters, resource: e.target.value })}
          >
            <option value="">All Resources</option>
            <option value="user_profile">User Profile</option>
            <option value="business_profile">Business Profile</option>
            <option value="assessment">Assessment</option>
            <option value="certificate">Certificate</option>
          </select>
          <input
            type="date"
            className="input"
            value={filters.date_from}
            onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
            placeholder="From Date"
          />
          <input
            type="date"
            className="input"
            value={filters.date_to}
            onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
            placeholder="To Date"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Timestamp</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">User</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Action</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Resource</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">Details</th>
              <th className="text-left py-3 px-4 font-medium text-slate-900">IP Address</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="6" className="text-center py-8">Loading audit logs...</td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center py-8 text-slate-500">No audit logs found</td>
              </tr>
            ) : logs.map(log => (
              <tr key={log.id} className="border-t hover:bg-slate-50">
                <td className="py-3 px-4 text-sm text-slate-600">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="py-3 px-4">
                  <div className="text-sm">
                    <div className="font-medium text-slate-900">{log.user_email || log.user_id}</div>
                    <div className="text-slate-600">{log.user_role}</div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(log.action)}`}>
                    {log.action}
                  </span>
                </td>
                <td className="py-3 px-4 text-sm text-slate-600">
                  {log.resource}
                </td>
                <td className="py-3 px-4 text-sm text-slate-600">
                  {log.details ? (
                    <details className="cursor-pointer">
                      <summary>View Changes</summary>
                      <pre className="mt-2 text-xs bg-slate-50 p-2 rounded">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </details>
                  ) : (
                    'No details'
                  )}
                </td>
                <td className="py-3 px-4 text-sm text-slate-600 font-mono">
                  {log.ip_address || 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getActionColor(action) {
  const colors = {
    'login': 'bg-green-100 text-green-800',
    'logout': 'bg-slate-100 text-slate-800',
    'profile_update': 'bg-blue-100 text-blue-800',
    'certificate_issued': 'bg-purple-100 text-purple-800',
    'assessment_completed': 'bg-orange-100 text-orange-800'
  };
  return colors[action] || 'bg-slate-100 text-slate-800';
}

// Additional admin components would go here...
// FeatureFlagsTab, BusinessProfilesTab, etc.

function FeatureFlagsTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Feature Flags</h2>
      <div className="text-center py-12 text-slate-500">
        Feature flag management coming soon...
      </div>
    </div>
  );
}

function BusinessProfilesTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Business Profiles</h2>
      <div className="text-center py-12 text-slate-500">
        Business profile management coming soon...
      </div>
    </div>
  );
}

function AssessmentsTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Assessment Management</h2>
      <div className="text-center py-12 text-slate-500">
        Assessment management coming soon...
      </div>
    </div>
  );
}

function CertificatesTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Certificate Management</h2>
      <div className="text-center py-12 text-slate-500">
        Certificate management coming soon...
      </div>
    </div>
  );
}

function SystemConfigTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">System Configuration</h2>
      <div className="text-center py-12 text-slate-500">
        System configuration coming soon...
      </div>
    </div>
  );
}

function DataGovernanceTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibent text-slate-900 mb-4">Data Governance</h2>
      <div className="text-center py-12 text-slate-500">
        Data governance tools coming soon...
      </div>
    </div>
  );
}

function RolesPermissionsTab() {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Roles & Permissions</h2>
      <div className="text-center py-12 text-slate-500">
        Role and permission management coming soon...
      </div>
    </div>
  );
}

export default AdminDashboard;