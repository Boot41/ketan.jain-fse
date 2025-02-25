import React from 'react';

function Features() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-12">
          Powerful Features for Your Jira Workflow
        </h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              title: 'AI-Powered Task Management',
              description: 'Automatically prioritize, categorize, and assign tasks based on historical data and team patterns.',
              icon: '🤖'
            },
            {
              title: 'Smart Issue Templates',
              description: 'AI-generated templates that adapt to your project needs and previous successful tickets.',
              icon: '📝'
            },
            {
              title: 'Automated Workflows',
              description: 'Intelligent workflow suggestions based on your team\'s most efficient patterns.',
              icon: '⚡'
            },
            {
              title: 'Natural Language Processing',
              description: 'Convert casual chat messages into structured Jira tickets automatically.',
              icon: '💬'
            },
            {
              title: 'Predictive Analytics',
              description: 'Forecast project timelines and potential bottlenecks before they occur.',
              icon: '📊'
            },
            {
              title: 'Smart Notifications',
              description: 'Context-aware alerts that keep you informed without overwhelming your inbox.',
              icon: '🔔'
            }
          ].map((feature, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Features;