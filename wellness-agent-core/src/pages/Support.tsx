import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Accordion, AccordionContent, AccordionItem, AccordionTrigger 
} from '@/components/ui/accordion';
import { HelpCircle, MessageCircle, Mail, Send, Smile, Meh, Frown } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Support = () => {
  const [feedback, setFeedback] = useState('');
  const [selectedRating, setSelectedRating] = useState<number | null>(null);
  const { toast } = useToast();

  const faqs = [
    {
      question: 'How accurate is the AI symptom checker?',
      answer: 'Our AI symptom checker uses advanced machine learning algorithms trained on extensive medical data. However, it should be used as a supplementary tool and not replace professional medical diagnosis. Always consult with a healthcare provider for accurate diagnosis and treatment.',
    },
    {
      question: 'Can I customize my diet plan?',
      answer: 'Yes! You can customize your diet plan by updating your preferences in the Profile section. Specify allergies, dietary restrictions (vegan, vegetarian, etc.), and health goals. The AI will automatically adjust meal recommendations.',
    },
    {
      question: 'How do I connect my wearable device?',
      answer: 'Go to Profile > Update Data > Lifestyle section and click "Connect Device." We support most major fitness trackers including Apple Watch, Fitbit, Garmin, and Samsung Galaxy Watch.',
    },
    {
      question: 'Is my health data secure?',
      answer: 'Absolutely. We use bank-level encryption and comply with HIPAA regulations. Your data is encrypted both in transit and at rest. We never share your personal health information without explicit consent.',
    },
    {
      question: 'How often should I update my health data?',
      answer: 'We recommend updating your health data whenever there are significant changes (new conditions, medications, or lifestyle changes). For best results, review and update your profile monthly.',
    },
    {
      question: 'Can I export my data?',
      answer: 'Yes! You can export all your health data, meal plans, and analytics as CSV or PDF files from the Analytics page or Settings.',
    },
    {
      question: 'How do I cancel my account?',
      answer: 'You can delete your account from Settings > Account. Please note this action is permanent and will delete all your data.',
    },
  ];

  const handleSubmitFeedback = () => {
    if (!feedback || selectedRating === null) {
      toast({
        title: 'Missing information',
        description: 'Please provide a rating and feedback.',
        variant: 'destructive',
      });
      return;
    }

    toast({
      title: 'Thank you!',
      description: 'Your feedback has been submitted successfully.',
    });
    setFeedback('');
    setSelectedRating(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-primary to-accent mb-4 shadow-glow">
            <HelpCircle className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold mb-3 gradient-text">Support & FAQ</h1>
          <p className="text-lg text-muted-foreground">
            Find answers to common questions or get in touch with us
          </p>
        </div>

        {/* Chat Bot Panel */}
        <div className="glass-card-elevated p-8 mb-8 animate-slide-up">
          <div className="flex items-start gap-4">
            <div className="p-4 rounded-2xl bg-gradient-warm shrink-0">
              <MessageCircle className="h-8 w-8 text-foreground" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">Ask Us Anything!</h2>
              <p className="text-muted-foreground mb-4">
                Our AI assistant is here 24/7 to help answer your questions instantly.
              </p>
              <div className="flex gap-3">
                <Input placeholder="Type your question here..." className="flex-1" />
                <Button variant="hero">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* FAQs */}
        <div className="mb-8 animate-slide-up" style={{ animationDelay: '100ms' }}>
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          <div className="glass-card-elevated overflow-hidden">
            <Accordion type="single" collapsible className="w-full">
              {faqs.map((faq, index) => (
                <AccordionItem key={index} value={`item-${index}`} className="border-b border-border last:border-0">
                  <AccordionTrigger className="px-6 py-4 hover:bg-muted/30 transition-colors">
                    <span className="text-left font-semibold">{faq.question}</span>
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4 text-muted-foreground">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        </div>

        {/* Contact Form */}
        <div className="glass-card-elevated p-8 mb-8 animate-slide-up" style={{ animationDelay: '200ms' }}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 rounded-xl bg-gradient-to-br from-secondary to-green-500">
              <Mail className="h-6 w-6 text-white" />
            </div>
            <h2 className="text-2xl font-bold">Still Need Help?</h2>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input placeholder="Your name" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <Input type="email" placeholder="your@email.com" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Subject</label>
              <Input placeholder="What can we help you with?" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Message</label>
              <Textarea 
                placeholder="Describe your issue or question..."
                rows={5}
              />
            </div>

            <Button variant="hero" className="w-full">
              <Send className="mr-2 h-4 w-4" />
              Send Message
            </Button>
          </div>
        </div>

        {/* Feedback Section */}
        <div className="glass-card-elevated p-8 animate-slide-up" style={{ animationDelay: '300ms' }}>
          <h2 className="text-2xl font-bold mb-6">Share Your Feedback</h2>
          
          <div className="space-y-6">
            <div>
              <p className="text-sm font-medium mb-4">How would you rate your experience?</p>
              <div className="flex justify-center gap-8">
                {[
                  { icon: Smile, label: 'Great', value: 3, color: 'text-secondary hover:text-secondary' },
                  { icon: Meh, label: 'Okay', value: 2, color: 'text-warm hover:text-warm' },
                  { icon: Frown, label: 'Poor', value: 1, color: 'text-destructive hover:text-destructive' },
                ].map((rating) => {
                  const Icon = rating.icon;
                  const isSelected = selectedRating === rating.value;
                  return (
                    <button
                      key={rating.value}
                      onClick={() => setSelectedRating(rating.value)}
                      className={`flex flex-col items-center gap-2 p-4 rounded-xl transition-all ${
                        isSelected 
                          ? 'bg-muted scale-110' 
                          : 'hover:bg-muted/50'
                      }`}
                    >
                      <Icon className={`h-12 w-12 ${rating.color}`} />
                      <span className="text-sm font-medium">{rating.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Tell us more (optional)</label>
              <Textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="What could we improve?"
                rows={4}
              />
            </div>

            <Button 
              variant="hero" 
              className="w-full" 
              onClick={handleSubmitFeedback}
            >
              Submit Feedback
            </Button>
          </div>
        </div>

        {/* Contact Info */}
        <div className="text-center mt-8 text-muted-foreground animate-fade-in">
          <p className="mb-2">
            Email us at <a href="mailto:support@aiwellness.com" className="text-primary hover:underline">support@aiwellness.com</a>
          </p>
          <p>
            Response time: Usually within 24 hours
          </p>
        </div>
      </div>
    </div>
  );
};

export default Support;
