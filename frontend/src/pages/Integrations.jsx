import React from 'react';

function Integrations() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-4">
          Seamless Integrations
        </h1>
        <p className="text-xl text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          Connect JiraAIAssistant with your favorite tools
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              name: 'Jira Cloud',
              description: 'Full integration with Atlassian\'s cloud-based project management solution.',
              features: ['Real-time sync', 'Smart workflows', 'Custom fields support']
            },
            {
              name: 'Jira Server',
              description: 'Secure integration with your self-hosted Jira instance.',
              features: ['VPN support', 'Custom security policies', 'Local data processing']
            },
            {
              name: 'Slack',
              description: 'Create and manage Jira issues directly from your Slack channels.',
              features: ['Command shortcuts', 'Rich previews', 'Channel notifications']
            },
            {
              name: 'Microsoft Teams',
              description: 'Seamless integration with your Microsoft Teams workspace.',
              features: ['Tab integration', 'Bot commands', 'Meeting insights']
            },
            {
              name: 'GitHub',
              description: 'Link commits and pull requests to Jira issues automatically.',
              features: ['Branch linking', 'PR status updates', 'Commit tracking']
            },
            {
              name: 'Bitbucket',
              description: 'Native integration with Atlassian\'s version control system.',
              features: ['Pipeline updates', 'Code insights', 'Deployment tracking']
            }
          ].map((integration, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-3">{integration.name}</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-4">{integration.description}</p>
              <ul className="space-y-2">
                {integration.features.map((feature, i) => (
                  <li key={i} className="flex items-center text-sm">
                    <span className="text-primary-600 dark:text-primary-400 mr-2">•</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Integrations;