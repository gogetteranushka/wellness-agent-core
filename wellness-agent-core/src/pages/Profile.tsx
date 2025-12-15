import React, { useState, useEffect } from 'react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MessageCircle, Bot, Activity, LogOut, User, Edit3, Save, X } from 'lucide-react';
import { supabase } from '../../supabaseClient';
import { useNavigate } from 'react-router-dom';

const UserDashboard = () => {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<any>({});
  const [updateLoading, setUpdateLoading] = useState(false);
  const [dietType, setDietType] = useState<string>('');
  const [dietGoal, setDietGoal] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
  }, []);

  async function fetchUserData() {
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        navigate('/auth');
        return;
      }

      const authUserName =
        `${user.user_metadata?.firstName || ''} ${user.user_metadata?.lastName || ''}`.trim() ||
        user.email?.split('@')[0] ||
        `User ${user.id.slice(-6)}`;

      const { data: profileData } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();

      const mergedProfile = {
        ...profileData,
        full_name: authUserName,
        email: user.email,
      };

      setProfile(mergedProfile);
      setEditData(profileData || {});

      try {
        const parsed =
          typeof profileData?.dietary_preferences === 'string'
            ? JSON.parse(profileData.dietary_preferences)
            : profileData?.dietary_preferences || {};
        setDietType(parsed.type || '');
        setDietGoal(parsed.goal || '');
      } catch {
        setDietType('');
        setDietGoal('');
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  }

  const handleEditToggle = () => {
    if (isEditing) {
      setIsEditing(false);
    } else {
      setEditData(profile);

      try {
        const parsed =
          typeof profile.dietary_preferences === 'string'
            ? JSON.parse(profile.dietary_preferences)
            : profile.dietary_preferences || {};
        setDietType(parsed.type || '');
        setDietGoal(parsed.goal || '');
      } catch {
        setDietType('');
        setDietGoal('');
      }

      setIsEditing(true);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setEditData((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleUpdateProfile = async () => {
    setUpdateLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();

      const newDietPrefs = {
        ...(typeof profile.dietary_preferences === 'string'
          ? JSON.parse(profile.dietary_preferences || '{}')
          : profile.dietary_preferences || {}),
        type: dietType || null,
        goal: dietGoal || null,
      };

      const { email, full_name, ...dbFields } = editData;

      const updated = {
        ...dbFields,
        dietary_preferences: newDietPrefs,
      };

      const { error } = await supabase
        .from('user_profiles')
        .update(updated)
        .eq('user_id', user!.id);

      if (error) throw error;

      setProfile({ ...profile, ...updated });
      setIsEditing(false);
      await fetchUserData();
    } catch (error: any) {
      console.error('Error updating profile:', error);
      alert(error.message || 'Failed to update profile. Please try again.');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditData(profile);
    setIsEditing(false);
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    window.location.href = '/auth';
  };

  // Navigation handlers
  const handleDietPlan = () => {
    navigate('/diet-plan');
  };

  const handleAIChat = () => {
    navigate('/ai-chatbot');
  };

  const handleSymptomChecker = () => {
    navigate('/symptom-checker');
  };

  const getDietPref = () => {
    if (!profile?.dietary_preferences) return 'Not set';
    try {
      const parsed =
        typeof profile.dietary_preferences === 'string'
          ? JSON.parse(profile.dietary_preferences)
          : profile.dietary_preferences;
      return [
        parsed.type ? `Type: ${parsed.type}` : null,
        parsed.goal ? `Goal: ${parsed.goal}` : null,
      ]
        .filter(Boolean)
        .join(', ');
    } catch {
      return profile.dietary_preferences || 'Not set';
    }
  };

  const bmi =
    profile?.weight && profile?.height
      ? (Number(profile.weight) / ((Number(profile.height) / 100) ** 2)).toFixed(1)
      : null;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="glass-card p-8 text-center">Loading your dashboard...</div>
      </div>
    );
  }

  if (!profile) {
    navigate('/onboarding');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Welcome Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-4 mb-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src={profile.avatar_url} />
              <AvatarFallback>{profile.email?.charAt(0).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Hello, {profile.full_name || `User ${profile.user_id.slice(-6)}`}!
              </h1>
              <p className="text-xl text-muted-foreground mt-2">
                Welcome back to your health dashboard
              </p>
            </div>
          </div>

          {/* Quick stats row */}
          <div className="flex flex-wrap gap-4 justify-center mt-2">
            <div className="px-4 py-2 rounded-full bg-white/70 shadow-sm text-sm flex items-center gap-2">
              <span className="font-semibold">BMI</span>
              <span className="text-muted-foreground">{bmi ?? '--'}</span>
            </div>
            <div className="px-4 py-2 rounded-full bg-white/70 shadow-sm text-sm flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="text-muted-foreground">
                Goal: {dietGoal || 'Not set'}
              </span>
            </div>
          </div>
        </div>

        {/* Profile Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="glass-card lg:col-span-2 max-w-4xl mx-auto">
            <CardHeader className="pb-2 relative">
              <div className="flex items-center gap-3 mb-2">
                <User className="h-6 w-6 text-blue-600" />
                <CardTitle className="text-2xl">Your Profile</CardTitle>
              </div>
              {!isEditing ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute top-4 right-4 h-8 w-8 p-0"
                  onClick={handleEditToggle}
                >
                  <Edit3 className="h-4 w-4" />
                </Button>
              ) : (
                <div className="flex gap-2 absolute top-4 right-4">
                  <Button
                    size="sm"
                    className="h-8 gap-1"
                    onClick={handleUpdateProfile}
                    disabled={updateLoading}
                  >
                    {updateLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        Save
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8"
                    onClick={handleCancelEdit}
                    disabled={updateLoading}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </CardHeader>

            <CardContent className="pt-2 pb-6">
              {isEditing ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">Age</Label>
                      <Input
                        type="number"
                        value={editData.age || ''}
                        onChange={(e) => handleInputChange('age', e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Gender</Label>
                      <Select
                        value={editData.gender || ''}
                        onValueChange={(value) => handleInputChange('gender', value)}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Height (cm)</Label>
                      <Input
                        type="number"
                        value={editData.height || ''}
                        onChange={(e) => handleInputChange('height', e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Weight (kg)</Label>
                      <Input
                        type="number"
                        step="0.1"
                        value={editData.weight || ''}
                        onChange={(e) => handleInputChange('weight', e.target.value)}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">Diet Type</Label>
                      <Select value={dietType} onValueChange={(value) => setDietType(value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select diet type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Vegetarian">Vegetarian</SelectItem>
                          <SelectItem value="Non-Vegetarian">Non-Vegetarian</SelectItem>
                          <SelectItem value="Vegan">Vegan</SelectItem>
                          <SelectItem value="Pescatarian">Pescatarian</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">Goal</Label>
                      <Select value={dietGoal} onValueChange={(value) => setDietGoal(value)}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select goal" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Weight Loss">Weight Loss</SelectItem>
                          <SelectItem value="Muscle Gain">Muscle Gain</SelectItem>
                          <SelectItem value="Maintenance">Maintenance</SelectItem>
                          <SelectItem value="General Health">General Health</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm items-start">
                    <div className="space-y-3">
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">
                          Age
                        </span>
                        <div className="font-semibold mt-1 text-lg">{profile.age}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">
                          Gender
                        </span>
                        <div className="font-semibold mt-1 capitalize">{profile.gender}</div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">
                          Height
                        </span>
                        <div className="font-semibold mt-1">{profile.height} cm</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">
                          Weight
                        </span>
                        <div className="font-semibold mt-1">{profile.weight} kg</div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">
                          BMI
                        </span>
                        <div className="font-semibold mt-1">{bmi ?? '--'}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">
                          Diet Preferences
                        </span>
                        <div className="mt-2">
                          <Badge variant="secondary" className="text-sm px-3 py-1 rounded-full">
                            {getDietPref()}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Health Modules */}
        <div className="mt-10 border-t border-border pt-10">
          <CardHeader className="pb-6">
            <CardTitle className="text-3xl font-bold text-center mb-2">
              Your Health Modules
            </CardTitle>
            <CardDescription className="text-center max-w-2xl mx-auto">
              Access personalized health tools powered by AI
            </CardDescription>
          </CardHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="glass-card group hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 h-full">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl text-center">AI Diet Plan</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-center mb-6">
                  Get personalized meal plans based on your profile and preferences
                </p>
                <Button className="w-full h-12 text-lg" size="lg" onClick={handleDietPlan}>
                  Generate Plan
                </Button>
              </CardContent>
            </Card>

            <Card className="glass-card group hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 h-full">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl text-center">AI Chatbot</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-center mb-6">
                  Ask health questions and get instant AI-powered responses
                </p>
                <Button className="w-full h-12 text-lg" size="lg" onClick={handleAIChat}>
                  Start Chat
                </Button>
              </CardContent>
            </Card>

            <Card className="glass-card group hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 h-full">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Activity className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-xl text-center">Symptom Checker</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground text-center mb-6">
                  Check symptoms and get preliminary health insights instantly
                </p>
                <Button className="w-full h-12 text-lg" size="lg" onClick={handleSymptomChecker}>
                  Check Symptoms
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Sign Out */}
        <div className="mt-16 text-center">
          <Button onClick={handleSignOut} variant="outline" size="lg" className="gap-2">
            <LogOut className="h-5 w-5" />
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
