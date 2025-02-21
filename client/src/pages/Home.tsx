import React, { useState } from 'react';
import { Bot, MessageSquare, GitCommit, BarChart3, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

function Home() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setEmail('');
      alert("Thanks for signing up! We'll be in touch soon.");
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <nav className="flex items-center justify-between mb-16">
          <div className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-blue-500" />
            <span className="text-2xl font-bold text-white">Autobot</span>
          </div>
          <div className="flex items-center space-x-4">
            <Link 
              to="/login"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Log in
            </Link>
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors">
              Get Started
            </button>
          </div>
        </nav>

        <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
          <div className="lg:w-1/2">
            <h1 className="text-4xl lg:text-6xl font-bold text-white mb-6">
              AI-Powered Project Management Assistant
            </h1>
            <p className="text-gray-300 text-lg mb-8">
              Transform your project management workflow with our intelligent Autobot. 
              Automatically create, categorize, and prioritize Jira tickets through natural conversations.
            </p>
            
            <form onSubmit={handleSubmit} className="flex gap-4 mb-8">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your work email"
                className="flex-1 px-4 py-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 border border-gray-600 focus:outline-none focus:border-blue-500"
                required
              />
              <button 
                type="submit"
                disabled={loading}
                className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Signing up...' : 'Sign Up Free'}
              </button>
            </form>

            <div className="flex items-center gap-2 text-gray-400">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>14-day free trial • No credit card required</span>
            </div>
          </div>

          <div className="lg:w-1/2">
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <img 
                src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80"
                alt="Dashboard Preview"
                className="rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Powerful Features for Modern Teams
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<MessageSquare className="h-6 w-6 text-blue-500" />}
            title="Conversational AI"
            description="Create Jira tickets through natural conversations with our AI assistant."
          />
          <FeatureCard 
            icon={<GitCommit className="h-6 w-6 text-blue-500" />}
            title="Context-Aware"
            description="Automatically extract relevant details from discussions and commits."
          />
          <FeatureCard 
            icon={<BarChart3 className="h-6 w-6 text-blue-500" />}
            title="Smart Analytics"
            description="Get insights on ticket trends and team performance."
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { 
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 hover:border-blue-500 transition-colors">
      <div className="bg-gray-700 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}

export default Home;