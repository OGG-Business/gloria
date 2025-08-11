# Multi-stage build pour le frontend React
FROM node:18-alpine AS builder

# Métadonnées
LABEL maintainer="SwiftPay Team <team@swiftpay.com>"
LABEL description="SwiftPay Frontend - Interface utilisateur React TypeScript"
LABEL version="1.0.0"

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Installer les dépendances
RUN npm ci --only=production --silent

# Copier le code source
COPY src ./src
COPY public ./public
COPY index.html ./

# Variables d'environnement pour le build
ARG VITE_API_BASE_URL=http://localhost:8080
ARG VITE_KEYCLOAK_URL=http://localhost:8180
ARG VITE_KEYCLOAK_REALM=swiftpay
ARG VITE_OAUTH2_CLIENT_ID=swiftpay-frontend

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_KEYCLOAK_URL=$VITE_KEYCLOAK_URL
ENV VITE_KEYCLOAK_REALM=$VITE_KEYCLOAK_REALM
ENV VITE_OAUTH2_CLIENT_ID=$VITE_OAUTH2_CLIENT_ID

# Construire l'application
RUN npm run build

# Stage de production avec Nginx
FROM nginx:1.25-alpine AS production

# Installer les outils nécessaires
RUN apk add --no-cache curl

# Copier la configuration Nginx
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers buildés
COPY --from=builder /app/dist /usr/share/nginx/html

# Copier le script d'entrée pour la configuration dynamique
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Créer un utilisateur non-root
RUN addgroup -g 1001 -S nginx-user && \
    adduser -S nginx-user -u 1001 -G nginx-user

# Ajuster les permissions
RUN chown -R nginx-user:nginx-user /usr/share/nginx/html && \
    chown -R nginx-user:nginx-user /var/cache/nginx && \
    chown -R nginx-user:nginx-user /var/log/nginx && \
    chown -R nginx-user:nginx-user /etc/nginx/conf.d

# Créer les répertoires pour les PID files
RUN mkdir -p /var/run/nginx && \
    chown -R nginx-user:nginx-user /var/run/nginx

# Exposer le port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Passer à l'utilisateur non-root
USER nginx-user

# Point d'entrée
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]