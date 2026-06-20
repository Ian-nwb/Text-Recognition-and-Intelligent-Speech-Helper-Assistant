# Stage 1: Build Flutter Web
FROM ubuntu:22.04 AS build

# Install build dependencies
RUN apt-get update && apt-get install -y \
  curl \
  git \
  unzip \
  xz-utils \
  zip \
  libglu1-mesa \
  && rm -rf /var/lib/apt/lists/*

# Clone the stable Flutter SDK
RUN git clone https://github.com/flutter/flutter.git -b stable /usr/local/flutter

# Add flutter to environment path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Initialize flutter and enable web support
RUN flutter doctor
RUN flutter config --enable-web

# Set working directory
WORKDIR /usr/src/app

# Copy pubspec files first to leverage Docker layer caching
COPY pubspec.yaml ./
# Check if lock file exists and copy it
COPY pubspec.lock* ./

# Download dependencies
RUN flutter pub get

# Copy the rest of the application code
COPY . .

# Build the web application in release mode
RUN flutter build web --release

# Stage 2: Serve built files with Nginx
FROM nginx:alpine
COPY --from=build /usr/src/app/build/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
