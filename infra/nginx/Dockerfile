FROM node:18-alpine AS builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json .
RUN npm install

# Include the .env file for build-time environment 

COPY frontend .
RUN npm run build-only


FROM jonasal/nginx-certbot:4.3-alpine

COPY infra/nginx/nginx.conf /etc/nginx/conf.d/scavengerhunt.conf
COPY --from=builder /app/dist /frontend

