import React from 'react';
import { Bot, Plus, Filter, Search, Clock, CheckCircle2, AlertCircle, BarChart2, Bell, MoreVertical } from 'lucide-react';
import { Link } from 'react-router-dom';

function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-gray-800 border-r border-gray-700">
        <div className="p-4">
          <Link to="/" className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-blue-500" />
            <span className="text-xl font-bold text-white">Autobot</span>
          </Link>
        </div>
        
        <nav className="mt-8">
          <div className="px-4 mb-2">
            <button className="w-full flex items-center justify-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
              <Plus className="h-5 w-5" />
              <span>New Ticket</span>
            </button>
          </div>
          
          <div className="px-2">
            {[
              { name: 'All Tickets', icon: Filter, count: 28 },
              { name: 'In Progress', icon: Clock, count: 12 },
              { name: 'Completed', icon: CheckCircle2, count: 8 },
              { name: 'Urgent', icon: AlertCircle, count: 3 },
              { name: 'Analytics', icon: BarChart2 },
            ].map((item) => (
              <a
                key={item.name}
                href="#"
                className="flex items-center justify-between px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </div>
                {item.count && (
                  <span className="bg-gray-700 text-xs px-2 py-1 rounded-full">
                    {item.count}
                  </span>
                )}
              </a>
            ))}
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700">
          <div className="flex items-center justify-between px-8 py-4">
            <div className="flex-1 max-w-2xl">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search tickets..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="text-gray-300 hover:text-white transition-colors">
                <span className="sr-only">Notifications</span>
                <div className="relative">
                  <div className="absolute -top-1 -right-1 h-2 w-2 bg-blue-500 rounded-full"></div>
                  <Bell className="h-6 w-6" />
                </div>
              </button>
              
              <button className="flex items-center space-x-2">
                <img
                  src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=facearea&facepad=2&w=48&h=48&q=80"
                  alt="User avatar"
                  className="h-8 w-8 rounded-full"
                />
                <span className="text-sm text-gray-300">John Doe</span>
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="p-8">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white mb-2">Welcome back, John!</h1>
            <p className="text-gray-400">Here's what's happening with your projects today.</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[
              { label: 'Total Tickets', value: '28', change: '+12%', up: true },
              { label: 'In Progress', value: '12', change: '-2%', up: false },
              { label: 'Completed Today', value: '8', change: '+8%', up: true },
              { label: 'Urgent Tasks', value: '3', change: '-5%', up: false },
            ].map((stat) => (
              <div key={stat.label} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <p className="text-sm text-gray-400">{stat.label}</p>
                <p className="text-2xl font-bold text-white mt-2">{stat.value}</p>
                <p className={`text-sm mt-2 ${stat.up ? 'text-green-500' : 'text-red-500'}`}>
                  {stat.change} from last week
                </p>
              </div>
            ))}
          </div>

          {/* Recent Tickets */}
          <div className="bg-gray-800 rounded-xl border border-gray-700">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">Recent Tickets</h2>
            </div>
            <div className="divide-y divide-gray-700">
              {[
                {
                  title: 'Implement AI-powered ticket categorization',
                  priority: 'High',
                  status: 'In Progress',
                  assignee: 'Sarah Chen',
                  avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=facearea&facepad=2&w=48&h=48&q=80',
                },
                {
                  title: 'Add real-time notifications for ticket updates',
                  priority: 'Medium',
                  status: 'To Do',
                  assignee: 'Michael Brown',
                  avatar: 'https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?auto=format&fit=facearea&facepad=2&w=48&h=48&q=80',
                },
                {
                  title: 'Optimize database queries for better performance',
                  priority: 'Low',
                  status: 'Done',
                  assignee: 'Emily Wilson',
                  avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=facearea&facepad=2&w=48&h=48&q=80',
                },
              ].map((ticket, i) => (
                <div key={i} className="p-6 hover:bg-gray-750 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h3 className="text-white font-medium">{ticket.title}</h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            ticket.priority === 'High' ? 'bg-red-500/10 text-red-500' :
                            ticket.priority === 'Medium' ? 'bg-yellow-500/10 text-yellow-500' :
                            'bg-green-500/10 text-green-500'
                          }`}>
                            {ticket.priority}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            ticket.status === 'Done' ? 'bg-green-500/10 text-green-500' :
                            ticket.status === 'In Progress' ? 'bg-blue-500/10 text-blue-500' :
                            'bg-gray-500/10 text-gray-400'
                          }`}>
                            {ticket.status}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <img
                          src={ticket.avatar}
                          alt={ticket.assignee}
                          className="h-8 w-8 rounded-full"
                        />
                        <span className="text-sm text-gray-400">{ticket.assignee}</span>
                      </div>
                      <button className="text-gray-400 hover:text-white transition-colors">
                        <MoreVertical className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Dashboard;