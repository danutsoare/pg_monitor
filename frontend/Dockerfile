# Frontend Dockerfile for React + TypeScript (Development)
FROM node:20-alpine

# Set the working directory
WORKDIR /app/client

# Copy package.json and install dependencies
# Copy package lock only if it exists
COPY client/package.json client/package-lock.json* ./
RUN npm install

# Copy the rest of the application code
# The volume mount in docker-compose will handle local changes
COPY client/ ./

# Expose the Vite default port
EXPOSE 5173

# Command to run the Vite development server
# --host is needed to expose the server to the host machine
CMD ["npm", "run", "dev", "--", "--host"]

# Production environment
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]