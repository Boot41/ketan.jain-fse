import { useState } from 'react';
import { Link } from 'react-router-dom';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

function Navbar({ theme, toggleTheme }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-lg">
      <div className="container-custom">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center">
            <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
              JiraAIAssistant
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            <Link to="/features" className="hover:text-primary-600 dark:hover:text-primary-400">Features</Link>
            <Link to="/pricing" className="hover:text-primary-600 dark:hover:text-primary-400">Pricing</Link>
            <Link to="/blog" className="hover:text-primary-600 dark:hover:text-primary-400">Blog</Link>
            <Link to="/contact" className="hover:text-primary-600 dark:hover:text-primary-400">Contact</Link>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              {theme === 'dark' ? (
                <SunIcon className="h-5 w-5" />
              ) : (
                <MoonIcon className="h-5 w-5" />
              )}
            </button>
            <Link to="/signup" className="btn-primary">
              Get Started
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <span className="sr-only">Open menu</span>
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={isOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'}
              />
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1">
              <Link
                to="/features"
                className="block px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Features
              </Link>
              <Link
                to="/pricing"
                className="block px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Pricing
              </Link>
              <Link
                to="/blog"
                className="block px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Blog
              </Link>
              <Link
                to="/contact"
                className="block px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Contact
              </Link>
              <Link
                to="/signup"
                className="block px-3 py-2 btn-primary text-center"
              >
                Get Started
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;