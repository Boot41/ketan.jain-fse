# Technology Stack

This document outlines the complete technology stack used in our project.

## Frontend Technologies

### Core
- **React** (v18.3.1) - A JavaScript library for building user interfaces
- **TypeScript** (v5.3.3) - Typed superset of JavaScript
- **Vite** (v5.0.12) - Next-generation frontend tooling

### Styling & UI
- **TailwindCSS** (v3.4.1) - Utility-first CSS framework
- **PostCSS** (v8.4.35) - Tool for transforming CSS with JavaScript
- **Lucide React** (v0.344.0) - Beautiful & consistent icons

### Routing
- **React Router DOM** (v6.22.3) - Declarative routing for React applications

### Development Tools

#### Code Quality
- **ESLint** (v8.56.0) - JavaScript/TypeScript linter
  - `@typescript-eslint/eslint-plugin` (v6.21.0)
  - `@typescript-eslint/parser` (v6.21.0)
  - `eslint-plugin-react` (v7.33.2)
  - `eslint-plugin-react-hooks` (v4.6.0)
  - `eslint-plugin-react-refresh` (v0.4.5)

#### Type Definitions
- **@types/react** (v18.3.5)
- **@types/react-dom** (v18.3.0)

## Development Environment

### Build Tools
- **Vite** - Build tool and development server
  - `@vitejs/plugin-react` (v4.2.1) - Official React plugin for Vite

### Containerization
- **Docker** - Container platform
  - Base Image: `node:20-alpine`
- **Docker Compose** (v3.8) - Multi-container orchestration

### Development Features
- Hot Module Replacement (HMR)
- TypeScript compilation
- ESLint integration
- PostCSS processing
- TailwindCSS compilation

## Project Configuration Files

### TypeScript
- `tsconfig.json` - Base TypeScript configuration
- `tsconfig.app.json` - Application-specific TypeScript settings
- `tsconfig.node.json` - Node-specific TypeScript settings

### Build & Development
- `vite.config.ts` - Vite configuration
- `postcss.config.js` - PostCSS configuration
- `tailwind.config.js` - TailwindCSS configuration
- `.eslintrc.cjs` - ESLint configuration

### Docker
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Container orchestration
- `.dockerignore` - Docker build exclusions

### Version Control
- Git
- `.gitignore` - Version control exclusions

## Development Practices

### Code Quality Standards
- Strict TypeScript checking
- ESLint rules enforcement
- React best practices
- Component-based architecture

### Type Safety
- TypeScript interfaces for props
- Strict null checks
- Type-safe event handlers
- Proper module declarations

### Component Organization
- Functional components
- React hooks
- Proper prop typing
- Modular CSS with TailwindCSS
