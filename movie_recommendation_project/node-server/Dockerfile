# Use the official Node.js image as the base image
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if it exists) to the container
COPY package*.json ./

# Install dependencies inside the container
RUN npm install

# Copy the rest of your application code to the container
COPY . .

# Expose port 3000 for the Node.js app
EXPOSE 3000

# Command to run the app
CMD ["node", "server.js"]