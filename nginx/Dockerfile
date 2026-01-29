FROM nginx:alpine

# Remove default configuration
RUN rm /etc/nginx/nginx.conf

# Copy custom configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
