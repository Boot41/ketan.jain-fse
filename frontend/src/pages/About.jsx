import React from 'react';

function About() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-4">
          About JiraAIAssistant
        </h1>
        <p className="text-xl text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          Transforming project management with AI-powered intelligence
        </p>

        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              We're on a mission to revolutionize how teams work with Jira by bringing the power of artificial intelligence to project management. Our goal is to make project management more efficient, intuitive, and productive for teams of all sizes.
            </p>
            <p className="text-gray-600 dark:text-gray-300">
              By combining cutting-edge AI technology with deep Jira expertise, we're creating tools that understand your team's needs and help you work smarter, not harder.
            </p>
          </div>
          <div className="bg-primary-50 dark:bg-gray-800 p-8 rounded-xl">
            <h3 className="text-xl font-semibold mb-4">Our Values</h3>
            <ul className="space-y-4">
              <li className="flex items-start">
                <span className="text-primary-600 dark:text-primary-400 mr-2">•</span>
                <div>
                  <strong className="block mb-1">Innovation First</strong>
                  <p className="text-gray-600 dark:text-gray-300">Constantly pushing the boundaries of what's possible with AI in project management</p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 dark:text-primary-400 mr-2">•</span>
                <div>
                  <strong className="block mb-1">User-Centric Design</strong>
                  <p className="text-gray-600 dark:text-gray-300">Building intuitive solutions that enhance rather than complicate workflows</p>
                </div>
              </li>
              <li className="flex items-start">
                <span className="text-primary-600 dark:text-primary-400 mr-2">•</span>
                <div>
                  <strong className="block mb-1">Security & Trust</strong>
                  <p className="text-gray-600 dark:text-gray-300">Maintaining the highest standards of data security and privacy</p>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 mb-16">
          <h2 className="text-2xl font-semibold mb-6 text-center">Our Team</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: 'Sarah Chen',
                role: 'CEO & Co-founder',
                bio: 'Former PM at Atlassian with 10+ years in project management tools'
              },
              {
                name: 'Michael Rodriguez',
                role: 'CTO & Co-founder',
                bio: 'AI researcher and engineer with expertise in natural language processing'
              },
              {
                name: 'Emily Thompson',
                role: 'Head of Product',
                bio: 'Product leader focused on creating intuitive user experiences'
              }
            ].map((member, index) => (
              <div key={index} className="text-center">
                <div className="w-24 h-24 bg-primary-100 dark:bg-primary-900 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl">{member.name.charAt(0)}</span>
                </div>
                <h3 className="font-semibold mb-2">{member.name}</h3>
                <p className="text-primary-600 dark:text-primary-400 mb-2">{member.role}</p>
                <p className="text-sm text-gray-600 dark:text-gray-300">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;