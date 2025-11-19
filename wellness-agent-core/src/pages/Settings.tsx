import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Settings as SettingsIcon, Bell, Lock, Download,
  Trash2, Moon, Sun, Shield, Database
} from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';

const Settings = () => {
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    weeklyReport: true,
    dietReminders: false,
    healthAlerts: true,
  });

  const [privacy, setPrivacy] = useState({
    analytics: true,
    sharing: false,
    twoFactor: false,
  });

  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const { toast } = useToast();

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
    toast({
      title: 'Settings updated',
      description: 'Your notification preferences have been saved.',
    });
    // TODO: Add backend API call to persist settings
  };

  const handlePrivacyChange = (key: string, value: boolean) => {
    setPrivacy(prev => ({ ...prev, [key]: value }));
    toast({
      title: 'Privacy settings updated',
      description: 'Your privacy preferences have been saved.',
    });
    // TODO: Add backend API call to persist settings
  };

  const handleExportData = () => {
    toast({
      title: 'Export started',
      description: 'Your data export will be ready shortly and sent to your email.',
    });
    // TODO: Trigger backend export API
  };

  const handleDeleteAccount = () => {
    toast({
      title: 'Account deleted',
      description: 'Your account and all associated data have been permanently deleted.',
      variant: 'destructive',
    });
    // TODO: Call backend API to delete account then sign user out
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
            <SettingsIcon className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-3 gradient-text">Settings</h1>
          <p className="text-lg text-muted-foreground">
            Manage your account preferences and privacy settings
          </p>
        </div>

        <div className="space-y-6">
          {/* Theme */}
          <div className="glass-card-elevated p-6 animate-slide-up">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-warm to-orange-500">
                {theme === 'light' ? (
                  <Sun className="h-6 w-6 text-white" />
                ) : (
                  <Moon className="h-6 w-6 text-white" />
                )}
              </div>
              <div>
                <h2 className="text-xl font-bold">Appearance</h2>
                <p className="text-sm text-muted-foreground">Customize how the app looks</p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-muted/50">
              <div>
                <Label htmlFor="theme-toggle" className="text-base font-medium">
                  Dark Mode
                </Label>
                <p className="text-sm text-muted-foreground">Switch between light and dark theme</p>
              </div>
              <Switch
                id="theme-toggle"
                checked={theme === 'dark'}
                onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')}
              />
            </div>
          </div>

          {/* Notifications */}
          <div className="glass-card-elevated p-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-primary to-primary-glow">
                <Bell className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Notifications</h2>
                <p className="text-sm text-muted-foreground">Manage how you receive updates</p>
              </div>
            </div>

            <div className="space-y-4">
              {[
                { key: 'email', label: 'Email Notifications', desc: 'Receive updates via email' },
                { key: 'push', label: 'Push Notifications', desc: 'Get real-time alerts' },
                { key: 'weeklyReport', label: 'Weekly Health Report', desc: 'Summary of your weekly progress' },
                { key: 'dietReminders', label: 'Diet Reminders', desc: 'Reminders for meal planning' },
                { key: 'healthAlerts', label: 'Health Alerts', desc: 'Important health notifications' },
              ].map((setting) => (
                <div key={setting.key} className="flex items-center justify-between p-4 rounded-xl bg-muted/50">
                  <div>
                    <Label htmlFor={setting.key} className="text-base font-medium">
                      {setting.label}
                    </Label>
                    <p className="text-sm text-muted-foreground">{setting.desc}</p>
                  </div>
                  <Switch
                    id={setting.key}
                    checked={notifications[setting.key as keyof typeof notifications]}
                    onCheckedChange={(checked) => handleNotificationChange(setting.key, checked)}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Privacy & Security */}
          <div className="glass-card-elevated p-6 animate-slide-up" style={{ animationDelay: '200ms' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-secondary to-green-500">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Privacy & Security</h2>
                <p className="text-sm text-muted-foreground">Control your data and security</p>
              </div>
            </div>

            <div className="space-y-4">
              {[
                {
                  key: 'analytics',
                  label: 'Usage Analytics',
                  desc: 'Help us improve by sharing anonymous usage data',
                  icon: Database,
                },
                {
                  key: 'sharing',
                  label: 'Data Sharing',
                  desc: 'Share health insights with healthcare providers',
                  icon: Database,
                },
                {
                  key: 'twoFactor',
                  label: 'Two-Factor Authentication',
                  desc: 'Add an extra layer of security',
                  icon: Lock,
                },
              ].map((setting) => (
                <div key={setting.key} className="flex items-center justify-between p-4 rounded-xl bg-muted/50">
                  <div>
                    <Label htmlFor={`privacy-${setting.key}`} className="text-base font-medium">
                      {setting.label}
                    </Label>
                    <p className="text-sm text-muted-foreground">{setting.desc}</p>
                  </div>
                  <Switch
                    id={`privacy-${setting.key}`}
                    checked={privacy[setting.key as keyof typeof privacy]}
                    onCheckedChange={(checked) => handlePrivacyChange(setting.key, checked)}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Data Management */}
          <div className="glass-card-elevated p-6 animate-slide-up" style={{ animationDelay: '300ms' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-accent to-purple-500">
                <Database className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Data Management</h2>
                <p className="text-sm text-muted-foreground">Export or delete your data</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-muted/50">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-medium">Export Your Data</h3>
                    <p className="text-sm text-muted-foreground">
                      Download all your health data in CSV or PDF format
                    </p>
                  </div>
                  <Button variant="outline" onClick={handleExportData}>
                    <Download className="mr-2 h-4 w-4" />
                    Export
                  </Button>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-medium text-destructive">Delete Account</h3>
                    <p className="text-sm text-muted-foreground">
                      Permanently delete your account and all associated data
                    </p>
                  </div>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This action cannot be undone. This will permanently delete your account
                          and remove all your data from our servers.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleDeleteAccount}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Yes, delete my account
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
