import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  User, Mail, Phone, MapPin, Calendar, Heart, Activity, 
  Apple, AlertCircle, Edit, Watch
} from 'lucide-react';

const Profile = () => {
  const user = {
    name: 'Sarah Chen',
    email: 'sarah.chen@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    joinDate: 'January 2024',
    avatar: '',
  };

  const demographics = [
    { label: 'Age', value: '32 years' },
    { label: 'Gender', value: 'Female' },
    { label: 'Height', value: '5\'6" (168 cm)' },
    { label: 'Weight', value: '145 lbs (66 kg)' },
    { label: 'Blood Type', value: 'O+' },
  ];

  const medicalHistory = [
    'Seasonal Allergies (2015)',
    'Vitamin D Deficiency (2022)',
    'Minor Surgery - Appendectomy (2018)',
  ];

  const lifestyle = [
    { icon: Activity, label: 'Exercise', value: '4x per week' },
    { icon: Apple, label: 'Diet', value: 'Vegetarian' },
    { icon: Heart, label: 'Sleep', value: '7-8 hours' },
  ];

  const allergies = ['Peanuts', 'Shellfish', 'Pollen'];
  const preferences = ['Vegetarian', 'Low Sodium', 'Organic'];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Card */}
      <div className="glass-card-elevated p-8 mb-8 animate-fade-in">
        <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
          <Avatar className="h-32 w-32 border-4 border-primary shadow-glow">
            <AvatarImage src={user.avatar} />
            <AvatarFallback className="text-3xl bg-gradient-to-br from-primary to-accent text-white">
              {user.name.split(' ').map(n => n[0]).join('')}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 text-center md:text-left">
            <h1 className="text-3xl font-bold mb-2">{user.name}</h1>
            <div className="space-y-2 text-muted-foreground mb-4">
              <div className="flex items-center gap-2 justify-center md:justify-start">
                <Mail className="h-4 w-4" />
                <span>{user.email}</span>
              </div>
              <div className="flex items-center gap-2 justify-center md:justify-start">
                <Phone className="h-4 w-4" />
                <span>{user.phone}</span>
              </div>
              <div className="flex items-center gap-2 justify-center md:justify-start">
                <MapPin className="h-4 w-4" />
                <span>{user.location}</span>
              </div>
              <div className="flex items-center gap-2 justify-center md:justify-start">
                <Calendar className="h-4 w-4" />
                <span>Joined {user.joinDate}</span>
              </div>
            </div>

            <div className="flex gap-3 justify-center md:justify-start">
              <Link to="/update-data">
                <Button variant="hero">
                  <Edit className="mr-2 h-4 w-4" />
                  Update Data
                </Button>
              </Link>
              <Link to="/settings">
                <Button variant="outline">Settings</Button>
              </Link>
            </div>
          </div>

          {/* Wearable Status */}
          <div className="glass-card p-4 text-center">
            <Watch className="h-8 w-8 mx-auto mb-2 text-primary" />
            <p className="text-sm font-medium mb-1">Wearable Device</p>
            <Badge variant="secondary" className="bg-secondary">Connected</Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Demographics */}
        <div className="glass-card p-6 animate-slide-up">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <User className="h-6 w-6 text-primary" />
            Demographics
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {demographics.map((item) => (
              <div key={item.label} className="p-4 rounded-xl bg-muted/50">
                <p className="text-sm text-muted-foreground mb-1">{item.label}</p>
                <p className="font-semibold">{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Medical History */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Heart className="h-6 w-6 text-primary" />
            Medical History
          </h2>
          <div className="space-y-3">
            {medicalHistory.map((item, index) => (
              <div key={index} className="p-4 rounded-xl bg-muted/50 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Lifestyle */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '200ms' }}>
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            Lifestyle
          </h2>
          <div className="space-y-4">
            {lifestyle.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="p-4 rounded-xl bg-muted/50 flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-gradient-to-br from-primary to-primary-glow">
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-muted-foreground">{item.label}</p>
                    <p className="font-semibold">{item.value}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Allergies & Preferences */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '300ms' }}>
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Apple className="h-6 w-6 text-primary" />
            Dietary Info
          </h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-3 text-destructive">Allergies</h3>
              <div className="flex flex-wrap gap-2">
                {allergies.map((allergy) => (
                  <Badge key={allergy} variant="destructive" className="px-3 py-1">
                    {allergy}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3 text-secondary">Preferences</h3>
              <div className="flex flex-wrap gap-2">
                {preferences.map((pref) => (
                  <Badge key={pref} className="px-3 py-1 bg-secondary text-secondary-foreground">
                    {pref}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
