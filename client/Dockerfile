# Development stage
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port 5173 (Vite's default port)
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev"]
