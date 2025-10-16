import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Activity, Apple, Book, ArrowRight, CheckCircle, Star, Play } from 'lucide-react';
import heroImage from '@/assets/hero-wellness.jpg';

const Home = () => {
  const features = [
    {
      icon: Activity,
      title: 'Symptom Checker',
      description: 'AI-powered symptom analysis with instant health insights and recommendations.',
      link: '/symptom-checker',
      color: 'from-primary to-primary-glow',
    },
    {
      icon: Apple,
      title: 'AI Diet Plan',
      description: 'Personalized meal plans tailored to your health goals and dietary needs.',
      link: '/diet-plan',
      color: 'from-secondary to-green-400',
    },
    {
      icon: Book,
      title: 'Condition Explorer',
      description: 'Discover relationships between conditions, nutrients, and foods.',
      link: '/explorer',
      color: 'from-accent to-purple-400',
    },
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Wellness Enthusiast',
      content: 'This platform transformed how I approach my health. The AI insights are incredibly accurate!',
      rating: 5,
    },
    {
      name: 'Michael Torres',
      role: 'Fitness Coach',
      content: 'The diet planning feature is outstanding. My clients love the personalized recommendations.',
      rating: 5,
    },
    {
      name: 'Emma Williams',
      role: 'Health Professional',
      content: 'A powerful tool for understanding health conditions and making informed decisions.',
      rating: 5,
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-hero opacity-10" />
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: `url(${heroImage})` }}
        />
        
        <div className="container relative mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6">
              Your Personal
              <span className="block gradient-text mt-2">AI Wellness Companion</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Harness the power of artificial intelligence to understand your health, 
              optimize your nutrition, and achieve your wellness goals.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link to="/symptom-checker">
                <Button variant="hero" size="lg" className="btn-glow">
                  Get Started <ArrowRight className="ml-2" />
                </Button>
              </Link>
              <Link to="/auth">
                <Button variant="outline" size="lg" className="glass-card">
                  Sign In
                </Button>
              </Link>
              <Button variant="ghost" size="lg" className="group">
                <Play className="mr-2 group-hover:scale-110 transition-transform" />
                Watch Demo
              </Button>
            </div>
          </div>
        </div>

        {/* Animated background elements */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12 animate-slide-up">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features for Your Health</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Comprehensive tools designed to help you take control of your wellness journey
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Link
                  key={feature.title}
                  to={feature.link}
                  className="group"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="glass-card-elevated p-8 h-full hover:scale-105 transition-all duration-300 cursor-pointer animate-scale-in">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} p-4 mb-6 group-hover:scale-110 transition-transform shadow-glow`}>
                      <Icon className="w-full h-full text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                    <p className="text-muted-foreground mb-4">{feature.description}</p>
                    <div className="flex items-center text-primary font-medium group-hover:gap-2 transition-all">
                      Explore <ArrowRight className="ml-1 group-hover:translate-x-1 transition-transform" size={16} />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-br from-muted/30 to-background">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="animate-slide-up">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Why Choose AI Wellness?
              </h2>
              <div className="space-y-4">
                {[
                  'Evidence-based AI recommendations',
                  'Personalized health insights',
                  'Comprehensive nutritional tracking',
                  'Easy-to-understand analytics',
                  'Privacy-focused and secure',
                ].map((benefit) => (
                  <div key={benefit} className="flex items-start gap-3">
                    <CheckCircle className="h-6 w-6 text-secondary shrink-0 mt-0.5" />
                    <span className="text-lg">{benefit}</span>
                  </div>
                ))}
              </div>
              <Link to="/profile">
                <Button variant="hero" size="lg" className="mt-8">
                  Create Your Profile <ArrowRight className="ml-2" />
                </Button>
              </Link>
            </div>

            <div className="glass-card-elevated p-8 animate-float">
              <div className="aspect-video bg-gradient-to-br from-primary/20 to-accent/20 rounded-xl flex items-center justify-center">
                <Play className="h-20 w-20 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mt-6 mb-2">See How It Works</h3>
              <p className="text-muted-foreground">
                Watch our comprehensive guide to understanding and using all the platform features.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Trusted by Thousands</h2>
            <p className="text-muted-foreground text-lg">
              Real stories from people transforming their health
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={testimonial.name}
                className="glass-card p-6 animate-slide-up"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 fill-warm text-warm" />
                  ))}
                </div>
                <p className="text-foreground mb-6 italic">"{testimonial.content}"</p>
                <div>
                  <div className="font-semibold">{testimonial.name}</div>
                  <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-hero opacity-10" />
        <div className="container relative mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Health?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users taking control of their wellness journey with AI-powered insights
          </p>
          <Link to="/auth">
            <Button variant="hero" size="lg" className="btn-glow">
              Get Started Free <ArrowRight className="ml-2" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
