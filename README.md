# React TypeScript Project

A modern React application built with TypeScript, Vite, and Docker.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js (v20 or later)
- npm

### Development with Docker
1. Clone the repository
2. Start the development environment:
   ```bash
   docker-compose up
   ```
3. Open http://localhost:5173 in your browser

### Local Development (without Docker)
1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 🛠 Tech Stack
- React 18
- TypeScript
- Vite
- TailwindCSS
- ESLint
- Docker

## 📁 Project Structure
```
client/
├── src/            # Source code
├── public/         # Static assets
├── Dockerfile      # Docker configuration
└── vite.config.ts  # Vite configuration
```

## 🧪 Development
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

## 🐳 Docker Commands
- `docker-compose up` - Start development environment
- `docker-compose down` - Stop development environment
- `docker-compose build` - Rebuild containers
