import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Activity, Apple, Book, ArrowRight, CheckCircle, Star, Play } from 'lucide-react';
import heroImage from '@/assets/hero-wellness.jpg';
import { supabase } from '../../supabaseClient';

const Home = () => {
  const [testimonials, setTestimonials] = useState([
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
  ]);
  const [features, setFeatures] = useState([
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
      title: 'AI Chatbot',
      description: 'Get instant answers to your nutrition and health questions with our AI assistant.',
      link: '/ai-chatbot',
      color: 'from-purple-400 to-pink-400',
    },
    {
      icon: Book,
      title: 'Condition Explorer',
      description: 'Discover relationships between conditions, nutrients, and foods.',
      link: '/explorer',
      color: 'from-accent to-purple-400',
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        // You can fetch dynamic testimonials or features here with an authenticated API call
        // const token = session?.access_token;
        // const resTestimonial = await fetch(...);
        // const newTestimonials = await resTestimonial.json();
        // setTestimonials(newTestimonials);
      } catch (err: any) {
        setError(err.message);
      }
      setLoading(false);
    }
    fetchData();
  }, []);

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
              <Link to="/auth">
                <Button variant="hero" size="lg" className="btn-glow">
                  Get Started <ArrowRight className="ml-2" />
                </Button>
              </Link>
              {/* <Link to="/auth">
                <Button variant="outline" size="lg" className="glass-card">
                  Sign In
                </Button>
              </Link> */}

              {/* <Button variant="ghost" size="lg" className="group">
                <Play className="mr-2 group-hover:scale-110 transition-transform" />
                Watch Demo
              </Button> */}
            </div>
            {loading && <p>Loading content...</p>}
            {error && <p className="text-red-600">{error}</p>}
          </div>
        </div>

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

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
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
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
      {/* Left: Why choose us */}
      <div className="animate-slide-up lg:pr-8">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Why Choose AI Wellness?
        </h2>
        <p className="text-muted-foreground mb-8 max-w-2xl">
          FitMind AI helps you understand how food and health conditions connect,
          using clear language and Indian meal examples so you can act on the
          advice immediately.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            'Evidence-based AI recommendations',
            'Personalized health insights',
            'Comprehensive nutritional guidance',
            'Condition-aware meal suggestions',
            'Privacy-focused and secure',
          ].map((benefit) => (
            <div key={benefit} className="flex items-start gap-3">
              <CheckCircle className="h-6 w-6 text-secondary shrink-0 mt-0.5" />
              <span className="text-base md:text-lg">{benefit}</span>
            </div>
          ))}
        </div>

        <Link to="/profile">
          <Button variant="hero" size="lg" className="mt-8">
            View Profile <ArrowRight className="ml-2" />
          </Button>
        </Link>
      </div>

      {/* Right: simple illustration card (no scores) */}
      <div className="glass-card-elevated p-8 lg:p-10 animate-float">
        <h3 className="text-xl font-semibold mb-3">
          Built for Everyday Use
        </h3>
        <p className="text-muted-foreground mb-6">
          Ask questions the way you naturally speak, like “What should I eat
          for breakfast with diabetes?” and get clear, practical answers in
          seconds.
        </p>

        <div className="space-y-3 text-sm">
          <div className="rounded-lg border bg-muted/40 p-3">
            <p className="font-semibold mb-1">Natural conversation</p>
            <p className="text-muted-foreground">
              Follow-up questions like “Can they eat sugar?” keep context from
              your earlier messages.
            </p>
          </div>
          <div className="rounded-lg border bg-muted/40 p-3">
            <p className="font-semibold mb-1">Condition-aware guidance</p>
            <p className="text-muted-foreground">
              Answers adapt when you mention age, gender, or health conditions
              such as diabetes or heart disease.
            </p>
          </div>
          <div className="rounded-lg border bg-muted/40 p-3">
            <p className="font-semibold mb-1">Clear next steps</p>
            <p className="text-muted-foreground">
              Suggestions are specific—meals, portions, and tips you can apply
              the same day.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>


      {/* Testimonials Section
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
      </section> */}

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
