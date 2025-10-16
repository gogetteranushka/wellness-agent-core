import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  LayoutDashboard, Search, Filter, Download, UserPlus, 
  AlertCircle, CheckCircle, TrendingUp, User 
} from 'lucide-react';

const Dashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const users = [
    {
      id: 1,
      name: 'John Martinez',
      email: 'john.m@example.com',
      status: 'healthy',
      lastVisit: '2024-01-15',
      riskLevel: 'low',
      conditions: ['Seasonal Allergies'],
      avatar: 'JM',
    },
    {
      id: 2,
      name: 'Emily Watson',
      email: 'emily.w@example.com',
      status: 'monitor',
      lastVisit: '2024-01-14',
      riskLevel: 'medium',
      conditions: ['Type 2 Diabetes', 'Hypertension'],
      avatar: 'EW',
    },
    {
      id: 3,
      name: 'Michael Chen',
      email: 'michael.c@example.com',
      status: 'healthy',
      lastVisit: '2024-01-13',
      riskLevel: 'low',
      conditions: [],
      avatar: 'MC',
    },
    {
      id: 4,
      name: 'Sarah Johnson',
      email: 'sarah.j@example.com',
      status: 'attention',
      lastVisit: '2024-01-12',
      riskLevel: 'high',
      conditions: ['Heart Disease', 'High Cholesterol'],
      avatar: 'SJ',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-secondary text-secondary-foreground';
      case 'monitor':
        return 'bg-warm text-foreground';
      case 'attention':
        return 'bg-destructive text-destructive-foreground';
      default:
        return 'bg-muted';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'low':
        return <CheckCircle className="h-4 w-4 text-secondary" />;
      case 'medium':
        return <AlertCircle className="h-4 w-4 text-warm" />;
      case 'high':
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 animate-fade-in">
          <div>
            <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
              <LayoutDashboard className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold mb-2 gradient-text">Admin Dashboard</h1>
            <p className="text-lg text-muted-foreground">
              Manage patient profiles and health data
            </p>
          </div>
          <div className="flex gap-3 mt-4 md:mt-0">
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export Data
            </Button>
            <Button variant="hero">
              <UserPlus className="mr-2 h-4 w-4" />
              Add User
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Total Users', value: '1,247', change: '+12%', icon: User, color: 'from-primary to-primary-glow' },
            { label: 'Active Today', value: '342', change: '+5%', icon: TrendingUp, color: 'from-secondary to-green-500' },
            { label: 'Requires Attention', value: '23', change: '-8%', icon: AlertCircle, color: 'from-warm to-orange-500' },
            { label: 'Healthy Status', value: '89%', change: '+3%', icon: CheckCircle, color: 'from-accent to-purple-500' },
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="glass-card-elevated p-6 animate-scale-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {stat.change}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            );
          })}
        </div>

        {/* Search and Filter */}
        <div className="glass-card p-6 mb-6 animate-slide-up">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users by name or email..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
          </div>
        </div>

        {/* Users Table */}
        <div className="glass-card-elevated overflow-hidden animate-fade-in">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="text-left p-4 font-semibold">User</th>
                  <th className="text-left p-4 font-semibold">Status</th>
                  <th className="text-left p-4 font-semibold">Risk Level</th>
                  <th className="text-left p-4 font-semibold">Conditions</th>
                  <th className="text-left p-4 font-semibold">Last Visit</th>
                  <th className="text-left p-4 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {users
                  .filter(user => 
                    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    user.email.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  .map((user) => (
                    <tr key={user.id} className="hover:bg-muted/30 transition-colors">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white">
                              {user.avatar}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-muted-foreground">{user.email}</p>
                          </div>
                        </div>
                      </td>
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
                        {user.conditions.length > 0 ? (
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
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            View
                          </Button>
                          <Button variant="ghost" size="sm">
                            Edit
                          </Button>
                        </div>
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
