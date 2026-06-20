# Stage 1: Build React frontend
FROM node:20-alpine AS build

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve React frontend via Nginx
FROM nginx:alpine

# Copy built assets from Stage 1
COPY --from=build /usr/src/app/dist /usr/share/nginx/html

# Copy custom Nginx configuration if needed, or default is fine
# Expose HTTP port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
