import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { supabase } from '../../supabaseClient';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchProfile() {
      setLoading(true);
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setLoading(false);
        return;
      }
      const { data } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();
      setProfile(data);
      setLoading(false);
    }
    fetchProfile();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    window.location.href = "/auth";
  };

  useEffect(() => {
    if (!loading && !profile) {
      navigate('/onboarding');
    }
  }, [loading, profile, navigate]);

  // Parse and display diet preferences as readable text
  let dietPref = "Not set";
  try {
    const parsed =
      typeof profile?.dietary_preferences === "string"
        ? JSON.parse(profile.dietary_preferences)
        : profile?.dietary_preferences || {};
    dietPref = [
      parsed.type ? `Type: ${parsed.type}` : null,
      parsed.goal ? `Goal: ${parsed.goal}` : null,
    ].filter(Boolean).join(", ");
  } catch {
    dietPref = profile?.dietary_preferences || "Not set";
  }

  if (loading) return <div className="p-8">Loading profile...</div>;
  if (!profile) return null; // Already redirected to onboarding

  return (
    <div className="max-w-lg mx-auto mt-12 glass-card p-8 space-y-6">
      <h1 className="text-3xl font-bold mb-2">Your Profile</h1>
      <ul className="space-y-2">
        <li>
          <span className="font-semibold">Age:</span> {profile.age}
        </li>
        <li>
          <span className="font-semibold">Gender:</span> {profile.gender}
        </li>
        <li>
          <span className="font-semibold">Height:</span> {profile.height}
        </li>
        <li>
          <span className="font-semibold">Weight:</span> {profile.weight}
        </li>
        <li>
          <span className="font-semibold">Diet Preferences:</span> {dietPref}
        </li>
      </ul>
      <Button onClick={handleSignOut} variant="outline">
        Sign Out
      </Button>
    </div>
  );
};

export default Profile;
