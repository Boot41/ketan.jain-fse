import React from 'react';

function HowItWorks() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-12">
          How JiraAIAssistant Works
        </h1>

        <div className="space-y-16">
          {[
            {
              step: 1,
              title: 'Connect Your Jira Instance',
              description: 'Seamlessly integrate JiraAIAssistant with your Jira Cloud or Server instance with just a few clicks.',
              icon: '🔗'
            },
            {
              step: 2,
              title: 'Train the AI Assistant',
              description: 'Our AI learns from your existing workflows, tickets, and team patterns to provide personalized assistance.',
              icon: '🧠'
            },
            {
              step: 3,
              title: 'Start Collaborating',
              description: 'Use natural language to create, update, and manage Jira issues through our intuitive chat interface.',
              icon: '💬'
            },
            {
              step: 4,
              title: 'Optimize Your Workflow',
              description: 'Receive AI-powered suggestions and insights to continuously improve your team\'s productivity.',
              icon: '📈'
            }
          ].map((step, index) => (
            <div key={index} className="flex flex-col md:flex-row items-center gap-8">
              <div className="flex-shrink-0 w-16 h-16 flex items-center justify-center text-4xl bg-primary-100 dark:bg-primary-900 rounded-full">
                {step.icon}
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">
                  Step {step.step}: {step.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 text-lg">
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default HowItWorks;