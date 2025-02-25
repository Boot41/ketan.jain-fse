import { Link } from 'react-router-dom';

function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-800 section-padding">
        <div className="container-custom">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              Transform Your Jira Workflow with AI-Powered Assistance
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              Streamline your project management with intelligent automation, smart suggestions, and seamless Jira integration.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link to="/signup" className="btn-primary">
                Get Started Free
              </Link>
              <Link to="/how-it-works" className="px-4 py-2 font-semibold text-primary-600 dark:text-primary-400 border-2 border-primary-600 dark:border-primary-400 rounded-lg hover:bg-primary-50 dark:hover:bg-gray-800 transition-colors duration-200">
                See How It Works
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Preview */}
      <section className="section-padding">
        <div className="container-custom">
          <h2 className="text-3xl font-bold text-center mb-12">
            Powerful Features for Modern Teams
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'AI-Powered Automation',
                description: 'Automate routine tasks and get intelligent suggestions for issue management.',
                icon: '🤖'
              },
              {
                title: 'Smart Workflows',
                description: 'Optimize your team\'s productivity with AI-driven workflow recommendations.',
                icon: '⚡'
              },
              {
                title: 'Seamless Integration',
                description: 'Works perfectly with Jira Cloud and Server, plus other tools you love.',
                icon: '🔄'
              }
            ].map((feature, index) => (
              <div key={index} className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 dark:bg-primary-700 section-padding">
        <div className="container-custom text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Transform Your Workflow?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of teams already using JiraAIAssistant to supercharge their productivity.
          </p>
          <Link to="/signup" className="inline-block px-8 py-3 bg-white text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors duration-200">
            Start Free Trial
          </Link>
        </div>
      </section>
    </div>
  );
}

export default Home;