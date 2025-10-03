# Use Node.js base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies first
COPY package*.json ./
RUN npm install

# Install nodemon globally for live reload
RUN npm install -g nodemon

# Copy the rest of the code
COPY . .

# Expose backend port
EXPOSE 8000

# Start with nodemon for hot reload
CMD ["npm","run","dev"]
