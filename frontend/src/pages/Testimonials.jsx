import React from 'react';

function Testimonials() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-4">
          Customer Success Stories
        </h1>
        <p className="text-xl text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          See how teams are transforming their workflow with JiraAIAssistant
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              name: 'Sarah Chen',
              role: 'Project Manager at TechCorp',
              image: 'https://i.pravatar.cc/150?img=1',
              quote: 'JiraAIAssistant has revolutionized how we manage our sprints. The AI suggestions are incredibly accurate and save us hours in planning.',
              company: 'TechCorp'
            },
            {
              name: 'Michael Rodriguez',
              role: 'Scrum Master at InnovateLabs',
              image: 'https://i.pravatar.cc/150?img=2',
              quote: 'The automated issue categorization and smart notifications have made our daily standups much more efficient. A game-changer for our team.',
              company: 'InnovateLabs'
            },
            {
              name: 'Emily Thompson',
              role: 'Product Owner at CloudScale',
              image: 'https://i.pravatar.cc/150?img=3',
              quote: 'The AI-powered insights help us make data-driven decisions about our product roadmap. It\'s like having a data analyst built into Jira.',
              company: 'CloudScale'
            },
            {
              name: 'David Kim',
              role: 'Engineering Lead at DevFlow',
              image: 'https://i.pravatar.cc/150?img=4',
              quote: 'Integration with our development tools was seamless. The automated workflow suggestions have significantly reduced our cycle time.',
              company: 'DevFlow'
            },
            {
              name: 'Lisa Patel',
              role: 'Support Team Lead at ServicePro',
              image: 'https://i.pravatar.cc/150?img=5',
              quote: 'Converting customer chats to Jira tickets automatically has transformed our support workflow. Response times are down by 40%.',
              company: 'ServicePro'
            },
            {
              name: 'James Wilson',
              role: 'CTO at StartupX',
              image: 'https://i.pravatar.cc/150?img=6',
              quote: 'The ROI was immediate. Our team spends less time on ticket management and more time on actual development.',
              company: 'StartupX'
            }
          ].map((testimonial, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <img
                  src={testimonial.image}
                  alt={testimonial.name}
                  className="w-12 h-12 rounded-full mr-4"
                />
                <div>
                  <h3 className="font-semibold">{testimonial.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{testimonial.role}</p>
                </div>
              </div>
              <p className="text-gray-600 dark:text-gray-300 mb-4">"{testimonial.quote}"</p>
              <p className="text-sm font-semibold text-primary-600 dark:text-primary-400">
                {testimonial.company}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Testimonials;