# Multi-stage Docker build for Subscription Renewal & Expense Tracker
# Stage 1: Build JAR using Maven and OpenJDK 17
FROM maven:3.9.9-eclipse-temurin-17 AS builder
WORKDIR /build

# Cache dependency layer
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source and package executable JAR
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Runtime image with minimal JRE
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# Run as non-root user for security best practice
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser
USER appuser

# Copy JAR from builder stage
COPY --from=builder /build/target/subscription-tracker-*.jar app.jar

# Expose default HTTP port
EXPOSE 8080

# Environment variables with container defaults
ENV SPRING_PROFILES_ACTIVE=mysql \
    DB_URL=jdbc:mysql://mysql:3306/subscription_db?createDatabaseIfNotExist=true&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC \
    DB_USERNAME=root \
    DB_PASSWORD=rootpassword \
    REDIS_HOST=redis \
    REDIS_PORT=6379

ENTRYPOINT ["java", "-jar", "app.jar"]
