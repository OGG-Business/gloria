# Build stage
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /workspace
COPY backend-spring/pom.xml .
RUN mvn -q -ntp -e -DskipTests dependency:go-offline
COPY backend-spring/src ./src
RUN mvn -q -ntp -DskipTests package

# Run stage
FROM eclipse-temurin:17-jre
WORKDIR /app
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -XX:InitialRAMPercentage=50.0 -Djava.security.egd=file:/dev/./urandom"
COPY --from=build /workspace/target/backend-spring-0.1.0.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar /app/app.jar"]