# Multi-stage build pour optimiser la taille de l'image
FROM eclipse-temurin:17-jdk-alpine AS builder

# Métadonnées
LABEL maintainer="SwiftPay Team <team@swiftpay.com>"
LABEL description="SwiftPay Backend - Plateforme de transferts bancaires SWIFT & IBAN"
LABEL version="1.0.0"

# Installer les dépendances nécessaires
RUN apk add --no-cache curl

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration Maven
COPY pom.xml .
COPY .mvn .mvn
COPY mvnw .

# Télécharger les dépendances (cache Docker layer)
RUN ./mvnw dependency:go-offline -B

# Copier le code source
COPY src ./src

# Construire l'application
RUN ./mvnw clean package -DskipTests -B

# Stage de production
FROM eclipse-temurin:17-jre-alpine AS production

# Installer les outils nécessaires pour la production
RUN apk add --no-cache \
    curl \
    openssl \
    ca-certificates \
    tzdata \
    && update-ca-certificates

# Créer un utilisateur non-root pour la sécurité
RUN addgroup -g 1001 -S swiftpay && \
    adduser -S swiftpay -u 1001 -G swiftpay

# Définir le répertoire de travail
WORKDIR /app

# Créer les répertoires nécessaires
RUN mkdir -p logs certificates keystore && \
    chown -R swiftpay:swiftpay /app

# Copier l'artefact depuis le stage builder
COPY --from=builder /app/target/*.jar app.jar

# Copier les scripts utilitaires
COPY --chown=swiftpay:swiftpay scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Configuration des variables d'environnement
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0" \
    SPRING_PROFILES_ACTIVE=docker \
    TZ=UTC \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Exposer les ports
EXPOSE 8080 8081

# Passer à l'utilisateur non-root
USER swiftpay

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8081/actuator/health || exit 1

# Point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["java", "-jar", "app.jar"]