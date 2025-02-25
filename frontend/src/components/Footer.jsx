import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="bg-gray-50 dark:bg-gray-800">
      <div className="container-custom py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8">
          <div className="col-span-2 lg:col-span-1">
            <Link to="/" className="text-xl font-bold text-primary-600 dark:text-primary-400">
              JiraAIAssistant
            </Link>
            <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
              Enhancing Jira workflows with AI-powered assistance
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/features" className="hover:text-primary-600 dark:hover:text-primary-400">Features</Link></li>
              <li><Link to="/pricing" className="hover:text-primary-600 dark:hover:text-primary-400">Pricing</Link></li>
              <li><Link to="/integrations" className="hover:text-primary-600 dark:hover:text-primary-400">Integrations</Link></li>
              <li><Link to="/use-cases" className="hover:text-primary-600 dark:hover:text-primary-400">Use Cases</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="hover:text-primary-600 dark:hover:text-primary-400">About Us</Link></li>
              <li><Link to="/blog" className="hover:text-primary-600 dark:hover:text-primary-400">Blog</Link></li>
              <li><Link to="/testimonials" className="hover:text-primary-600 dark:hover:text-primary-400">Testimonials</Link></li>
              <li><Link to="/contact" className="hover:text-primary-600 dark:hover:text-primary-400">Contact</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/how-it-works" className="hover:text-primary-600 dark:hover:text-primary-400">How It Works</Link></li>
              <li><Link to="/faq" className="hover:text-primary-600 dark:hover:text-primary-400">FAQ</Link></li>
              <li><a href="#" className="hover:text-primary-600 dark:hover:text-primary-400">Documentation</a></li>
              <li><a href="#" className="hover:text-primary-600 dark:hover:text-primary-400">API Reference</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © {new Date().getFullYear()} JiraAIAssistant. All rights reserved.
            </p>
            <div className="mt-4 md:mt-0 flex space-x-6">
              <a href="#" className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">
                Privacy Policy
              </a>
              <a href="#" className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;