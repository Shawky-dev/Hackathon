FROM node:20

WORKDIR /app

# Copy package.json + package-lock.json first (if they exist)
# This layer is cached, so it won't reinstall deps unless these files change
COPY package*.json ./

RUN npm install

# Copy the rest of the frontend source
COPY . .

CMD ["npm", "run", "dev"]
