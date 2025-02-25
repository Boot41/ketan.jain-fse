import React from 'react';
import { Link } from 'react-router-dom';

function Pricing() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-4">
          Simple, Transparent Pricing
        </h1>
        <p className="text-xl text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          Choose the plan that best fits your team's needs
        </p>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              name: 'Starter',
              price: '29',
              description: 'Perfect for small teams getting started',
              features: [
                'Up to 10 team members',
                'Basic AI assistance',
                'Standard support',
                'Core integrations'
              ]
            },
            {
              name: 'Professional',
              price: '79',
              description: 'Ideal for growing teams and organizations',
              features: [
                'Up to 50 team members',
                'Advanced AI features',
                'Priority support',
                'All integrations',
                'Custom workflows',
                'Analytics dashboard'
              ],
              popular: true
            },
            {
              name: 'Enterprise',
              price: 'Custom',
              description: 'For large organizations with specific needs',
              features: [
                'Unlimited team members',
                'Custom AI training',
                '24/7 dedicated support',
                'Custom integrations',
                'Advanced security',
                'SLA guarantee'
              ]
            }
          ].map((plan, index) => (
            <div
              key={index}
              className={`relative bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 ${
                plan.popular ? 'ring-2 ring-primary-600 dark:ring-primary-400' : ''
              }`}
            >
              {plan.popular && (
                <span className="absolute top-0 right-0 -translate-y-1/2 px-3 py-1 bg-primary-600 text-white text-sm font-semibold rounded-full">
                  Most Popular
                </span>
              )}
              <h3 className="text-2xl font-semibold mb-2">{plan.name}</h3>
              <div className="mb-4">
                <span className="text-4xl font-bold">${plan.price}</span>
                {plan.price !== 'Custom' && <span className="text-gray-600 dark:text-gray-300">/month</span>}
              </div>
              <p className="text-gray-600 dark:text-gray-300 mb-6">{plan.description}</p>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center">
                    <svg className="w-5 h-5 text-primary-600 dark:text-primary-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                to="/signup"
                className={`block text-center py-2 px-4 rounded-lg font-semibold transition-colors duration-200 ${
                  plan.popular
                    ? 'bg-primary-600 text-white hover:bg-primary-700'
                    : 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 dark:border-primary-400 dark:text-primary-400 dark:hover:bg-gray-700'
                }`}
              >
                Get Started
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Pricing;