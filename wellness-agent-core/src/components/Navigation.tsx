import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  Menu, X, Heart, Home, Activity, Apple, BarChart3, 
  Book, LayoutDashboard, HelpCircle, Settings, User,
  MessageCircle  // ← ADD THIS IMPORT
} from 'lucide-react';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/symptom-checker', label: 'Symptoms', icon: Activity },
    { path: '/diet-plan', label: 'Diet Plan', icon: Apple },
    { path: '/ai-chatbot', label: 'AI Chat', icon: MessageCircle }, // ← ADD THIS
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/explorer', label: 'Explorer', icon: Book },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 glass-card border-b border-white/20">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary to-accent transition-transform group-hover:scale-110">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text hidden sm:block">
              AI Wellness
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link key={item.path} to={item.path}>
                  <Button
                    variant={isActive(item.path) ? 'default' : 'ghost'}
                    className={`${
                      isActive(item.path) 
                        ? 'btn-glow' 
                        : 'hover:bg-primary/10'
                    } transition-all duration-300`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.label}
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* Right side buttons */}
          <div className="hidden md:flex items-center space-x-2">
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                <LayoutDashboard className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <Link to="/settings">
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
              </Button>
            </Link>
            <Link to="/support">
              <Button variant="ghost" size="icon">
                <HelpCircle className="h-5 w-5" />
              </Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4 animate-slide-up">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsOpen(false)}
                  >
                    <Button
                      variant={isActive(item.path) ? 'default' : 'ghost'}
                      className={`w-full justify-start ${
                        isActive(item.path) ? 'btn-glow' : ''
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {item.label}
                    </Button>
                  </Link>
                );
              })}
              <div className="pt-2 border-t border-border space-y-2">
                <Link to="/dashboard" onClick={() => setIsOpen(false)}>
                  <Button variant="outline" className="w-full justify-start">
                    <LayoutDashboard className="h-4 w-4 mr-2" />
                    Dashboard
                  </Button>
                </Link>
                <Link to="/support" onClick={() => setIsOpen(false)}>
                  <Button variant="ghost" className="w-full justify-start">
                    <HelpCircle className="h-4 w-4 mr-2" />
                    Support
                  </Button>
                </Link>
                <Link to="/settings" onClick={() => setIsOpen(false)}>
                  <Button variant="ghost" className="w-full justify-start">
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
