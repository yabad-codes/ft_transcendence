FROM nginx:1.27

# Create directory for SSL certificates
RUN mkdir /etc/nginx/ssl

# Generate a self-signed SSL certificate non-interactively
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/selfsigned.key \
    -out /etc/nginx/ssl/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"

# Expose port 443 for SSL
EXPOSE 443

# Copy the custom NGINX configuration file into the appropriate directory
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Run NGINX in the foreground
CMD ["nginx", "-g", "daemon off;"]
