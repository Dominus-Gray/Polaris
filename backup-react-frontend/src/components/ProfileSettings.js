import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { DarkModeToggle, useDarkMode } from './DarkModeSupport';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function ProfileSettings() {
  const [activeTab, setActiveTab] = useState('personal');
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await axios.get(`${API}/profiles/me`);
      setProfile(response.data);
    } catch (error) {
      toast.error('Failed to load profile', { description: error.message });
    } finally {
      setLoading(false);
    }
  };

  const saveProfile = async (updates) => {
    setSaving(true);
    try {
      const response = await axios.patch(`${API}/profiles/me`, updates);
      setProfile(response.data);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile', { description: error.response?.data?.detail || error.message });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-6">
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6">
            <div className="animate-pulse">
              <div className="h-8 bg-slate-200 rounded mb-4"></div>
              <div className="space-y-3">
                <div className="h-4 bg-slate-200 rounded"></div>
                <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                <div className="h-4 bg-slate-200 rounded w-1/2"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Profile Settings</h1>
        <p className="text-slate-600 mt-1">Manage your account preferences and security settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1">
          <nav className="bg-white rounded-lg shadow-sm border p-4">
            <div className="space-y-1">
              <SettingsNavItem 
                icon="👤" 
                label="Personal Info" 
                id="personal"
                active={activeTab === 'personal'}
                onClick={() => setActiveTab('personal')}
              />
              <SettingsNavItem 
                icon="🔒" 
                label="Security" 
                id="security"
                active={activeTab === 'security'}
                onClick={() => setActiveTab('security')}
              />
              <SettingsNavItem 
                icon="🔔" 
                label="Notifications" 
                id="notifications"
                active={activeTab === 'notifications'}
                onClick={() => setActiveTab('notifications')}
              />
              <SettingsNavItem 
                icon="🎨" 
                label="Preferences" 
                id="preferences"
                active={activeTab === 'preferences'}
                onClick={() => setActiveTab('preferences')}
              />
              <SettingsNavItem 
                icon="🛡️" 
                label="Privacy" 
                id="privacy"
                active={activeTab === 'privacy'}
                onClick={() => setActiveTab('privacy')}
              />
              <SettingsNavItem 
                icon="📊" 
                label="Data & Export" 
                id="data"
                active={activeTab === 'data'}
                onClick={() => setActiveTab('data')}
              />
            </div>
          </nav>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border">
            {activeTab === 'personal' && (
              <PersonalInfoTab profile={profile} onSave={saveProfile} saving={saving} />
            )}
            {activeTab === 'security' && (
              <SecurityTab profile={profile} onSave={saveProfile} saving={saving} />
            )}
            {activeTab === 'notifications' && (
              <NotificationsTab profile={profile} onSave={saveProfile} saving={saving} />
            )}
            {activeTab === 'preferences' && (
              <PreferencesTab profile={profile} onSave={saveProfile} saving={saving} />
            )}
            {activeTab === 'privacy' && (
              <PrivacyTab profile={profile} onSave={saveProfile} saving={saving} />
            )}
            {activeTab === 'data' && (
              <DataExportTab profile={profile} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingsNavItem({ icon, label, id, active, onClick }) {
  return (
    <button
      className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg transition-colors ${
        active 
          ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-500' 
          : 'hover:bg-slate-50 text-slate-700'
      }`}
      onClick={onClick}
    >
      <span className="text-lg">{icon}</span>
      <span className="font-medium">{label}</span>
    </button>
  );
}

function PersonalInfoTab({ profile, onSave, saving }) {
  const [form, setForm] = useState({
    display_name: profile?.display_name || '',
    bio: profile?.bio || '',
    phone_number: profile?.phone_number || '',
    time_zone: profile?.time_zone || 'America/Chicago'
  });
  const [avatar, setAvatar] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API}/profiles/me/avatar`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setAvatar(response.data.avatar_url);
      toast.success('Avatar updated successfully');
    } catch (error) {
      toast.error('Failed to upload avatar', { description: error.message });
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Personal Information</h2>
        <p className="text-slate-600">Update your personal details and profile information.</p>
      </div>

      {/* Avatar Section */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 mb-2">Profile Picture</label>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full overflow-hidden bg-slate-100 border-2 border-slate-200">
            {avatar || profile?.avatar_url ? (
              <img 
                src={avatar || profile?.avatar_url} 
                alt="Profile" 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-400 text-xl font-semibold">
                {profile?.display_name?.[0]?.toUpperCase() || '?'}
              </div>
            )}
          </div>
          <div>
            <input
              type="file"
              accept="image/*"
              onChange={handleAvatarUpload}
              className="hidden"
              id="avatar-upload"
              disabled={uploading}
            />
            <label
              htmlFor="avatar-upload"
              className={`btn ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {uploading ? 'Uploading...' : 'Change Picture'}
            </label>
            <p className="text-xs text-slate-500 mt-1">JPG, PNG or GIF. Max size 5MB.</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Display Name *</label>
          <input
            type="text"
            className="input w-full"
            value={form.display_name}
            onChange={(e) => setForm({ ...form, display_name: e.target.value })}
            placeholder="Enter your display name"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Phone Number</label>
          <input
            type="tel"
            className="input w-full"
            value={form.phone_number}
            onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
            placeholder="(555) 123-4567"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-2">Bio</label>
          <textarea
            className="input w-full"
            rows="3"
            value={form.bio}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
            placeholder="Tell others about yourself..."
          />
          <p className="text-xs text-slate-500 mt-1">Brief description for your profile. Visible to other users.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Time Zone</label>
          <select
            className="input w-full"
            value={form.time_zone}
            onChange={(e) => setForm({ ...form, time_zone: e.target.value })}
          >
            <option value="America/New_York">Eastern Time (ET)</option>
            <option value="America/Chicago">Central Time (CT)</option>
            <option value="America/Denver">Mountain Time (MT)</option>
            <option value="America/Los_Angeles">Pacific Time (PT)</option>
            <option value="America/Anchorage">Alaska Time (AKT)</option>
            <option value="Pacific/Honolulu">Hawaii Time (HST)</option>
          </select>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button
          type="submit"
          className="btn btn-primary px-6"
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
}

function SecurityTab({ profile, onSave, saving }) {
  const [mfaEnabled, setMfaEnabled] = useState(profile?.two_factor_enabled || false);
  const [trustedDevices, setTrustedDevices] = useState([]);
  const [showPasswordChange, setShowPasswordChange] = useState(false);

  useEffect(() => {
    loadTrustedDevices();
  }, []);

  const loadTrustedDevices = async () => {
    try {
      const response = await axios.get(`${API}/security/trusted-devices`);
      setTrustedDevices(response.data);
    } catch (error) {
      console.error('Failed to load trusted devices:', error);
    }
  };

  const setupMFA = async () => {
    try {
      const response = await axios.post(`${API}/security/mfa/setup`);
      // Handle MFA setup flow with QR code
      toast.success('MFA setup initiated');
    } catch (error) {
      toast.error('Failed to setup MFA', { description: error.message });
    }
  };

  const revokeTrustedDevice = async (deviceId) => {
    try {
      await axios.delete(`${API}/security/trusted-devices/${deviceId}`);
      setTrustedDevices(devices => devices.filter(d => d.id !== deviceId));
      toast.success('Device access revoked');
    } catch (error) {
      toast.error('Failed to revoke device', { description: error.message });
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Security Settings</h2>
        <p className="text-slate-600">Manage your account security and access controls.</p>
      </div>

      {/* Password Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-900">Password</h3>
            <p className="text-sm text-slate-600">Change your account password</p>
          </div>
          <button
            className="btn"
            onClick={() => setShowPasswordChange(!showPasswordChange)}
          >
            Change Password
          </button>
        </div>

        {showPasswordChange && (
          <div className="border rounded-lg p-4 bg-slate-50">
            <PasswordChangeForm onComplete={() => setShowPasswordChange(false)} />
          </div>
        )}
      </div>

      {/* Two-Factor Authentication */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold text-slate-900">Two-Factor Authentication</h3>
            <p className="text-sm text-slate-600">
              Add an extra layer of security to your account
            </p>
          </div>
          <div className="flex items-center gap-3">
            {mfaEnabled && <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Enabled</span>}
            <button
              className={`btn ${mfaEnabled ? 'btn-secondary' : 'btn-primary'}`}
              onClick={setupMFA}
            >
              {mfaEnabled ? 'Manage MFA' : 'Enable MFA'}
            </button>
          </div>
        </div>
      </div>

      {/* Trusted Devices */}
      <div className="mb-8">
        <div className="mb-4">
          <h3 className="font-semibold text-slate-900">Trusted Devices</h3>
          <p className="text-sm text-slate-600">
            Devices that don't require two-factor authentication
          </p>
        </div>

        <div className="space-y-3">
          {trustedDevices.map(device => (
            <div key={device.id} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center">
                  {device.device_type === 'mobile' ? '📱' : '💻'}
                </div>
                <div>
                  <div className="font-medium text-slate-900">{device.device_name}</div>
                  <div className="text-sm text-slate-600">
                    Last seen: {new Date(device.last_seen).toLocaleDateString()}
                  </div>
                </div>
              </div>
              <button
                className="text-red-600 hover:text-red-700 text-sm font-medium"
                onClick={() => revokeTrustedDevice(device.id)}
              >
                Revoke
              </button>
            </div>
          ))}

          {trustedDevices.length === 0 && (
            <div className="text-center py-8 text-slate-500">
              No trusted devices configured
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PasswordChangeForm({ onComplete }) {
  const [form, setForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (form.new_password !== form.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/security/change-password`, {
        current_password: form.current_password,
        new_password: form.new_password
      });
      toast.success('Password changed successfully');
      onComplete();
    } catch (error) {
      toast.error('Failed to change password', { description: error.response?.data?.detail });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Current Password</label>
        <input
          type="password"
          className="input w-full"
          value={form.current_password}
          onChange={(e) => setForm({ ...form, current_password: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">New Password</label>
        <input
          type="password"
          className="input w-full"
          value={form.new_password}
          onChange={(e) => setForm({ ...form, new_password: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Confirm New Password</label>
        <input
          type="password"
          className="input w-full"
          value={form.confirm_password}
          onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
          required
        />
      </div>

      <div className="flex gap-3">
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Changing...' : 'Change Password'}
        </button>
        <button type="button" className="btn" onClick={onComplete}>
          Cancel
        </button>
      </div>
    </form>
  );
}

function NotificationsTab({ profile, onSave, saving }) {
  const [notifications, setNotifications] = useState(() => {
    const defaultSettings = {
      email_notifications: {
        assessment_reminders: true,
        provider_matches: true,
        certificate_issued: true,
        system_updates: false
      },
      sms_notifications: {
        urgent_only: true,
        assessment_deadlines: false,
        provider_responses: false
      },
      push_notifications: {
        enabled: true,
        assessment_progress: true,
        new_opportunities: true,
        provider_updates: true
      },
      in_app_notifications: {
        enabled: true,
        show_badges: true,
        auto_mark_read: false
      }
    };
    
    // Safely merge with existing settings
    if (profile?.notification_settings) {
      return {
        email_notifications: { ...defaultSettings.email_notifications, ...profile.notification_settings.email_notifications },
        sms_notifications: { ...defaultSettings.sms_notifications, ...profile.notification_settings.sms_notifications },
        push_notifications: { ...defaultSettings.push_notifications, ...profile.notification_settings.push_notifications },
        in_app_notifications: { ...defaultSettings.in_app_notifications, ...profile.notification_settings.in_app_notifications }
      };
    }
    
    return defaultSettings;
  });

  const handleSave = () => {
    onSave({ notification_settings: notifications });
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Notification Preferences</h2>
        <p className="text-slate-600">Choose how you want to be notified about important updates.</p>
      </div>

      {/* Email Notifications */}
      <div className="mb-8">
        <h3 className="font-semibold text-slate-900 mb-4">Email Notifications</h3>
        <div className="space-y-3">
          <NotificationToggle
            label="Assessment Reminders"
            description="Reminders for incomplete assessments"
            checked={notifications.email_notifications.assessment_reminders}
            onChange={(checked) => setNotifications({
              ...notifications,
              email_notifications: {
                ...notifications.email_notifications,
                assessment_reminders: checked
              }
            })}
          />
          <NotificationToggle
            label="Provider Matches"
            description="New provider matches for your requirements"
            checked={notifications.email_notifications.provider_matches}
            onChange={(checked) => setNotifications({
              ...notifications,
              email_notifications: {
                ...notifications.email_notifications,
                provider_matches: checked
              }
            })}
          />
          <NotificationToggle
            label="Certificate Issued"
            description="When your procurement certificate is ready"
            checked={notifications.email_notifications.certificate_issued}
            onChange={(checked) => setNotifications({
              ...notifications,
              email_notifications: {
                ...notifications.email_notifications,
                certificate_issued: checked
              }
            })}
          />
        </div>
      </div>

      {/* SMS Notifications */}
      <div className="mb-8">
        <h3 className="font-semibold text-slate-900 mb-4">SMS Notifications</h3>
        <div className="space-y-3">
          <NotificationToggle
            label="Urgent Only"
            description="Only critical security and system alerts"
            checked={notifications.sms_notifications.urgent_only}
            onChange={(checked) => setNotifications({
              ...notifications,
              sms_notifications: {
                ...notifications.sms_notifications,
                urgent_only: checked
              }
            })}
          />
        </div>
      </div>

      {/* Push Notifications */}
      <div className="mb-8">
        <h3 className="font-semibold text-slate-900 mb-4">Push Notifications</h3>
        <div className="space-y-3">
          <NotificationToggle
            label="Enable Push Notifications"
            description="Allow browser notifications from Polaris"
            checked={notifications.push_notifications.enabled}
            onChange={(checked) => setNotifications({
              ...notifications,
              push_notifications: {
                ...notifications.push_notifications,
                enabled: checked
              }
            })}
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          className="btn btn-primary px-6"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
}

function NotificationToggle({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div>
        <div className="font-medium text-slate-900">{label}</div>
        <div className="text-sm text-slate-600">{description}</div>
      </div>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          className="sr-only peer"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
      </label>
    </div>
  );
}

function PreferencesTab({ profile, onSave, saving }) {
  const { isDarkMode, userPreference, setTheme } = useDarkMode();
  const [preferences, setPreferences] = useState(
    profile?.preferences || {
      language: 'en',
      date_format: 'MM/dd/yyyy',
      currency: 'USD',
      dashboard_widgets: ['readiness_score', 'opportunities', 'assessment_progress']
    }
  );

  const handleSave = () => {
    onSave({ preferences });
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Preferences</h2>
        <p className="text-slate-600">Customize your Polaris experience.</p>
      </div>

      {/* Theme Settings */}
      <div className="mb-8 p-6 bg-slate-50 rounded-lg border">
        <div className="mb-4">
          <h3 className="text-lg font-medium text-slate-900 mb-2">Appearance</h3>
          <p className="text-sm text-slate-600">Customize the look and feel of your Polaris dashboard.</p>
        </div>
        
        {/* Dark Mode Toggle Component */}
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium text-slate-900">Theme</div>
            <div className="text-sm text-slate-600 mt-1">
              Current: {isDarkMode ? 'Dark Mode' : 'Light Mode'} 
              {userPreference === 'system' && ' (Following System)'}
            </div>
          </div>
          <DarkModeToggle />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Language</label>
          <select
            className="input w-full"
            value={preferences.language}
            onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
          >
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Date Format</label>
          <select
            className="input w-full"
            value={preferences.date_format}
            onChange={(e) => setPreferences({ ...preferences, date_format: e.target.value })}
          >
            <option value="MM/dd/yyyy">MM/DD/YYYY (US)</option>
            <option value="dd/MM/yyyy">DD/MM/YYYY (EU)</option>
            <option value="yyyy-MM-dd">YYYY-MM-DD (ISO)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Currency</label>
          <select
            className="input w-full"
            value={preferences.currency}
            onChange={(e) => setPreferences({ ...preferences, currency: e.target.value })}
          >
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
            <option value="GBP">GBP (£)</option>
            <option value="CAD">CAD (C$)</option>
          </select>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button
          className="btn btn-primary px-6"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
}

function PrivacyTab({ profile, onSave, saving }) {
  const [privacy, setPrivacy] = useState(
    profile?.privacy_settings || {
      profile_visibility: 'contacts_only',
      show_certification_status: true,
      allow_provider_contact: true,
      share_anonymized_data: false,
      data_retention_preference: 'standard'
    }
  );

  const handleSave = () => {
    onSave({ privacy_settings: privacy });
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Privacy Settings</h2>
        <p className="text-slate-600">Control how your information is shared and used.</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Profile Visibility</label>
          <select
            className="input w-full"
            value={privacy.profile_visibility}
            onChange={(e) => setPrivacy({ ...privacy, profile_visibility: e.target.value })}
          >
            <option value="public">Public - Visible to all users</option>
            <option value="contacts_only">Contacts Only - Visible to connected providers/agencies</option>
            <option value="private">Private - Only visible to you</option>
          </select>
          <p className="text-xs text-slate-500 mt-1">
            Controls who can see your profile information and contact you.
          </p>
        </div>

        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <div className="font-medium text-slate-900">Show Certification Status</div>
            <div className="text-sm text-slate-600">
              Display your procurement readiness score and certificates publicly
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={privacy.show_certification_status}
              onChange={(e) => setPrivacy({ ...privacy, show_certification_status: e.target.checked })}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div>
            <div className="font-medium text-slate-900">Allow Provider Contact</div>
            <div className="text-sm text-slate-600">
              Let service providers contact you about relevant opportunities
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={privacy.allow_provider_contact}
              onChange={(e) => setPrivacy({ ...privacy, allow_provider_contact: e.target.checked })}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Data Retention</label>
          <select
            className="input w-full"
            value={privacy.data_retention_preference}
            onChange={(e) => setPrivacy({ ...privacy, data_retention_preference: e.target.value })}
          >
            <option value="minimal">Minimal - Delete inactive data after 1 year</option>
            <option value="standard">Standard - Delete inactive data after 3 years</option>
            <option value="extended">Extended - Keep data until account deletion</option>
          </select>
          <p className="text-xs text-slate-500 mt-1">
            How long to retain your data after account inactivity.
          </p>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button
          className="btn btn-primary px-6"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Privacy Settings'}
        </button>
      </div>
    </div>
  );
}

function DataExportTab({ profile }) {
  const [exportRequests, setExportRequests] = useState([]);
  const [requesting, setRequesting] = useState(false);

  const requestDataExport = async () => {
    setRequesting(true);
    try {
      const response = await axios.post(`${API}/profiles/me/data-export`);
      toast.success('Data export requested', { 
        description: 'You will receive an email when your export is ready.' 
      });
      // Refresh export requests list
    } catch (error) {
      toast.error('Failed to request export', { description: error.message });
    } finally {
      setRequesting(false);
    }
  };

  const requestAccountDeletion = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await axios.post(`${API}/profiles/me/data-deletion`);
      toast.success('Account deletion requested', { 
        description: 'Please check your email to confirm this action.' 
      });
    } catch (error) {
      toast.error('Failed to request deletion', { description: error.message });
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-900 mb-2">Data & Export</h2>
        <p className="text-slate-600">Manage your data and account lifecycle.</p>
      </div>

      {/* Data Export */}
      <div className="mb-8">
        <div className="border rounded-lg p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Export Your Data</h3>
              <p className="text-sm text-slate-600">
                Download a copy of all your data including profile, assessments, and certificates.
              </p>
            </div>
            <button
              className="btn btn-primary"
              onClick={requestDataExport}
              disabled={requesting}
            >
              {requesting ? 'Requesting...' : 'Request Export'}
            </button>
          </div>
          
          <div className="text-xs text-slate-500">
            • Export includes: Profile data, business information, assessment results, certificates, and activity logs<br/>
            • Data will be provided in JSON format<br/>
            • Export will be available for download for 30 days<br/>
            • You will receive an email notification when ready
          </div>
        </div>
      </div>

      {/* Account Deletion */}
      <div className="mb-8">
        <div className="border border-red-200 rounded-lg p-6 bg-red-50">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="font-semibold text-red-900 mb-2">Delete Account</h3>
              <p className="text-sm text-red-700">
                Permanently delete your account and all associated data. This action cannot be undone.
              </p>
            </div>
            <button
              className="btn bg-red-600 text-white hover:bg-red-700"
              onClick={requestAccountDeletion}
            >
              Delete Account
            </button>
          </div>
          
          <div className="text-xs text-red-600">
            • All your data will be permanently deleted<br/>
            • Certificates and assessments will be invalidated<br/>
            • Provider connections will be removed<br/>
            • This action requires email confirmation
          </div>
        </div>
      </div>

      {/* Previous Export Requests */}
      {exportRequests.length > 0 && (
        <div>
          <h3 className="font-semibold text-slate-900 mb-4">Recent Export Requests</h3>
          <div className="space-y-2">
            {exportRequests.map(request => (
              <div key={request.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium text-slate-900">
                    Data Export - {new Date(request.created_at).toLocaleDateString()}
                  </div>
                  <div className="text-sm text-slate-600">Status: {request.status}</div>
                </div>
                {request.download_url && (
                  <a
                    href={request.download_url}
                    className="btn btn-sm"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfileSettings;