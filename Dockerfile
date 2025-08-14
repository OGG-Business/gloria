# Stage 1: Build the application using Maven
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean install -DskipTests

# Stage 2: Create the final, smaller image
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
# Argument to expose the port
ARG EXPOSE_PORT=8080
# Copy the executable JAR from the build stage
COPY --from=build /app/target/*.jar app.jar
EXPOSE ${EXPOSE_PORT}
ENTRYPOINT ["java", "-jar", "app.jar"]
