import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { LayoutDashboard, Search, Filter, Download, UserPlus, AlertCircle, CheckCircle } from 'lucide-react';
import { supabase } from '../../supabaseClient';

const Dashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  async function fetchUsers() {
    setLoading(true);
    setError(null);

    try {
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        setError('Please log in to view dashboard');
        setLoading(false);
        return;
      }

      // Fetch user profiles with only columns that exist
      const { data: profiles, error: profileError } = await supabase
        .from('user_profiles')
        .select(`
          user_id,
          age,
          gender,
          height,
          weight,
          dietary_preferences,
          created_at,
          updated_at
        `);
      if (profileError) throw profileError;

      const { data: conditions, error: conditionsError } = await supabase
        .from('user_conditions')
        .select('user_id, condition_name');
      if (conditionsError) throw conditionsError;

      // Construct output for each user
      const usersWithData = profiles.map(profile => {
        const userConditions = conditions
          .filter(c => c.user_id === profile.user_id)
          .map(c => c.condition_name);

        const riskLevel = userConditions.length >= 2 ? 'high' : userConditions.length === 1 ? 'medium' : 'low';
        const status = riskLevel === 'high' ? 'attention' : riskLevel === 'medium' ? 'monitor' : 'healthy';

        return {
          id: profile.user_id,
          name: `User ${profile.user_id.slice(0, 8)}`,
          age: profile.age,
          gender: profile.gender,
          height: profile.height,
          weight: profile.weight,
          status,
          riskLevel,
          conditions: userConditions,
          lastVisit: profile.updated_at || profile.created_at,
        };
      });

      setUsers(usersWithData);
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    }

    setLoading(false);
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-secondary text-secondary-foreground';
      case 'monitor': return 'bg-warm text-foreground';
      case 'attention': return 'bg-destructive text-destructive-foreground';
      default: return 'bg-muted';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'low': return <CheckCircle className="h-4 w-4 text-secondary" />;
      case 'medium': return <AlertCircle className="h-4 w-4 text-warm" />;
      case 'high': return <AlertCircle className="h-4 w-4 text-destructive" />;
      default: return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        {/* ...existing header code... */}
        {/* Search and Filter */}
        {/* ...existing search/filter code... */}
        {/* Loading/Error feedback */}
        {loading && <p>Loading users...</p>}
        {error && <p className="text-red-600">{error}</p>}
        {/* Users Table */}
        <div className="glass-card-elevated overflow-hidden animate-fade-in">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="text-left p-4 font-semibold">User</th>
                  <th className="text-left p-4 font-semibold">Age</th>
                  <th className="text-left p-4 font-semibold">Gender</th>
                  <th className="text-left p-4 font-semibold">Height</th>
                  <th className="text-left p-4 font-semibold">Weight</th>
                  <th className="text-left p-4 font-semibold">Status</th>
                  <th className="text-left p-4 font-semibold">Risk Level</th>
                  <th className="text-left p-4 font-semibold">Conditions</th>
                  <th className="text-left p-4 font-semibold">Last Visit</th>
                  <th className="text-left p-4 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {users
                  .filter(
                    (user) =>
                      user.name.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .map((user) => (
                    <tr key={user.id} className="hover:bg-muted/30 transition-colors">
                      <td className="p-4">{user.name}</td>
                      <td className="p-4">{user.age}</td>
                      <td className="p-4">{user.gender}</td>
                      <td className="p-4">{user.height}</td>
                      <td className="p-4">{user.weight}</td>
                      <td className="p-4">
                        <Badge className={getStatusColor(user.status)} variant="secondary">
                          {user.status}
                        </Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          {getRiskIcon(user.riskLevel)}
                          <span className="capitalize text-sm">{user.riskLevel}</span>
                        </div>
                      </td>
                      <td className="p-4">
                        {user.conditions?.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {user.conditions.map((condition, i) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                {condition}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-sm text-muted-foreground">None</span>
                        )}
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{user.lastVisit}</span>
                      </td>
                      <td className="p-4">
                        <Button variant="outline" size="sm">View</Button>
                        <Button variant="ghost" size="sm">Edit</Button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
