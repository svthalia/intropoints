# ---------------------- #
# -- -- Setup Node -- -- #
# ---------------------- #

# Import latest node version
#   - Recently bumped to v.20;
FROM node:22-alpine AS builder

# Setup working directory
WORKDIR /app
COPY package.json ./
RUN npm install

COPY . ./
RUN npm run build

# ----------------------- #
# -- -- Setup Proxy -- -- #
# ----------------------- #

# Setup internal frontend proxy
FROM nginx
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*

# Setup environment and entrypoint
COPY --from=builder /app/dist ./
COPY /resources/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY /resources/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Mark entrypoint for setup
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Allow proxy visibility over files
RUN chown nginx:nginx /usr/share/nginx/html/*

# Pass the proxy command to the entry point
CMD ["nginx", "-g", "daemon off;"]
