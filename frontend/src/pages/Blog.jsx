import React from 'react';

function Blog() {
  return (
    <div className="section-padding">
      <div className="container-custom">
        <h1 className="text-4xl font-bold text-center mb-4">
          Latest Insights & Updates
        </h1>
        <p className="text-xl text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          Stay up to date with AI-powered project management
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              title: 'The Future of AI in Project Management',
              excerpt: 'Explore how artificial intelligence is transforming the way teams manage projects and collaborate.',
              author: 'Sarah Chen',
              date: 'March 15, 2024',
              category: 'AI Insights'
            },
            {
              title: 'Maximizing Productivity with Smart Workflows',
              excerpt: 'Learn how to leverage automated workflows to reduce manual tasks and boost team efficiency.',
              author: 'Michael Rodriguez',
              date: 'March 12, 2024',
              category: 'Best Practices'
            },
            {
              title: 'New Feature: Advanced Analytics Dashboard',
              excerpt: 'Introducing our new analytics dashboard with predictive insights and team performance metrics.',
              author: 'Emily Thompson',
              date: 'March 10, 2024',
              category: 'Product Updates'
            },
            {
              title: 'Building Better Sprint Plans with AI',
              excerpt: 'Tips and strategies for using AI to improve sprint planning and estimation accuracy.',
              author: 'David Kim',
              date: 'March 8, 2024',
              category: 'Agile Methods'
            },
            {
              title: 'Customer Success Story: TechCorp',
              excerpt: 'How TechCorp improved their project delivery time by 40% using JiraAIAssistant.',
              author: 'Lisa Patel',
              date: 'March 5, 2024',
              category: 'Case Studies'
            },
            {
              title: 'Security Best Practices for AI Tools',
              excerpt: 'Essential security considerations when implementing AI-powered tools in your workflow.',
              author: 'James Wilson',
              date: 'March 3, 2024',
              category: 'Security'
            }
          ].map((post, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
              <div className="p-6">
                <div className="text-sm text-primary-600 dark:text-primary-400 mb-2">
                  {post.category}
                </div>
                <h3 className="text-xl font-semibold mb-3">{post.title}</h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {post.excerpt}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                  <span>{post.author}</span>
                  <span>{post.date}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Blog;