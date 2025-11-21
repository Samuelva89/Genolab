# --- Stage 1: Build Stage ---
# Use a Node.js image to build the project
FROM node:20-alpine AS build-stage

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package.json package-lock.json ./

# Install dependencies using 'npm ci' for reproducible builds
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Build the application
# This command will generate the 'dist' folder with static assets
RUN npm run build


# --- Stage 2: Production Stage ---
# Use a lightweight Nginx image to serve the static files
FROM nginx:stable-alpine AS production-stage

# Copy the custom Nginx configuration file created earlier
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the built static files from the 'build-stage'
# The source path (/app/dist) is from the previous stage
# The destination path (/usr/share/nginx/html) is the default Nginx root
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose the port defined in nginx.conf
EXPOSE 8080

# The default Nginx image command will start the server, so no CMD is needed
# CMD ["nginx", "-g", "daemon off;"]
