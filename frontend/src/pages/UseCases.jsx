import React from 'react';

function UseCases() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-12">
          Use Cases
        </h1>

        <div className="grid md:grid-cols-2 gap-8">
          {[
            {
              title: 'Agile Development Teams',
              description: 'Streamline sprint planning, backlog grooming, and daily standups with AI-powered insights and automation.',
              examples: [
                'Automated sprint velocity predictions',
                'Smart story point suggestions',
                'Daily standup summaries'
              ]
            },
            {
              title: 'Project Managers',
              description: 'Get comprehensive project oversight and proactive issue management through intelligent monitoring.',
              examples: [
                'Resource allocation optimization',
                'Risk prediction and mitigation',
                'Automated progress reports'
              ]
            },
            {
              title: 'Support Teams',
              description: 'Convert customer conversations into well-structured tickets and get smart routing suggestions.',
              examples: [
                'Automatic ticket categorization',
                'Priority level prediction',
                'Similar issue detection'
              ]
            },
            {
              title: 'Product Teams',
              description: 'Track feature requests, manage product backlog, and prioritize development efforts efficiently.',
              examples: [
                'Feature impact analysis',
                'User feedback clustering',
                'Release planning assistance'
              ]
            }
          ].map((useCase, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-semibold mb-4">{useCase.title}</h3>
              <p className="text-gray-600 dark:text-gray-300 mb-6">{useCase.description}</p>
              <ul className="space-y-2">
                {useCase.examples.map((example, i) => (
                  <li key={i} className="flex items-center">
                    <span className="text-primary-600 dark:text-primary-400 mr-2">→</span>
                    {example}
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

export default UseCases;