import React from 'react';

function FAQ() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-4">
          Frequently Asked Questions
        </h1>
        <p className="text-xl text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          Find answers to common questions about JiraAIAssistant
        </p>

        <div className="max-w-3xl mx-auto space-y-6">
          {[
            {
              question: 'How does JiraAIAssistant work with existing Jira installations?',
              answer: 'JiraAIAssistant seamlessly integrates with both Jira Cloud and Server through secure APIs. Once connected, it starts learning from your team\'s patterns and providing intelligent assistance immediately.'
            },
            {
              question: 'Is my data secure with JiraAIAssistant?',
              answer: 'Yes, we take security seriously. All data is encrypted in transit and at rest, and we comply with SOC 2 and GDPR requirements. We never store your Jira credentials, and you can revoke access at any time.'
            },
            {
              question: 'Can I customize the AI\'s behavior?',
              answer: 'Absolutely! JiraAIAssistant learns from your team\'s specific patterns and preferences. You can also configure custom rules, workflows, and preferences to match your organization\'s needs.'
            },
            {
              question: 'What kind of support do you offer?',
              answer: 'We offer different levels of support based on your plan. All customers get access to our documentation and community forums. Professional and Enterprise plans include priority support and dedicated account management.'
            },
            {
              question: 'How long does it take to set up?',
              answer: 'Basic setup takes just a few minutes. The AI starts providing value immediately and becomes more accurate as it learns from your team\'s patterns over time.'
            },
            {
              question: 'Can I try JiraAIAssistant before purchasing?',
              answer: 'Yes! We offer a 14-day free trial with full access to all features. No credit card required to start.'
            }
          ].map((faq, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-3">{faq.question}</h3>
              <p className="text-gray-600 dark:text-gray-300">{faq.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default FAQ;