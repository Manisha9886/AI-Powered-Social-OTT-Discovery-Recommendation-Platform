FROM node:18-alpine

WORKDIR /app

# Copy package.json and install
COPY package.json ./
RUN npm install

# Copy source
COPY . .

CMD ["npm", "run", "dev"]
