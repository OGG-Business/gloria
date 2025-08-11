package com.banking.transfers.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entité représentant un événement de transfert
 */
@Entity
@Table(name = "transfer_events", indexes = {
    @Index(name = "idx_transfer_event_transfer_id", columnList = "transfer_id"),
    @Index(name = "idx_transfer_event_type", columnList = "event_type"),
    @Index(name = "idx_transfer_event_created_at", columnList = "created_at")
})
@EntityListeners(AuditingEntityListener.class)
public class TransferEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transfer_id", nullable = false)
    @NotNull(message = "Le transfert est obligatoire")
    private Transfer transfer;

    @Enumerated(EnumType.STRING)
    @Column(name = "event_type", nullable = false, length = 50)
    @NotNull(message = "Le type d'événement est obligatoire")
    private EventType eventType;

    @Column(name = "event_code", length = 20)
    private String eventCode;

    @Column(name = "description", length = 500)
    private String description;

    @Column(name = "details", columnDefinition = "TEXT")
    private String details;

    @Column(name = "error_code", length = 20)
    private String errorCode;

    @Column(name = "error_message", length = 500)
    private String errorMessage;

    @Column(name = "source_system", length = 50)
    private String sourceSystem;

    @Column(name = "external_reference", length = 100)
    private String externalReference;

    @Column(name = "user_id", length = 100)
    private String userId;

    @Column(name = "user_name", length = 100)
    private String userName;

    @Column(name = "ip_address", length = 45)
    private String ipAddress;

    @Column(name = "user_agent", length = 500)
    private String userAgent;

    @Column(name = "session_id", length = 100)
    private String sessionId;

    @Column(name = "trace_id", length = 100)
    private String traceId;

    @Column(name = "correlation_id", length = 100)
    private String correlationId;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // Constructeurs
    public TransferEvent() {}

    public TransferEvent(Transfer transfer, EventType eventType, String description) {
        this.transfer = transfer;
        this.eventType = eventType;
        this.description = description;
    }

    public TransferEvent(Transfer transfer, EventType eventType, String eventCode, String description) {
        this.transfer = transfer;
        this.eventType = eventType;
        this.eventCode = eventCode;
        this.description = description;
    }

    // Méthodes utilitaires
    public boolean isError() {
        return EventType.ERROR.equals(this.eventType) || 
               EventType.FAILED.equals(this.eventType) || 
               EventType.REJECTED.equals(this.eventType);
    }

    public boolean isSuccess() {
        return EventType.COMPLETED.equals(this.eventType) || 
               EventType.ACCEPTED.equals(this.eventType) || 
               EventType.SENT.equals(this.eventType);
    }

    public boolean isInfo() {
        return EventType.INFO.equals(this.eventType) || 
               EventType.CREATED.equals(this.eventType) || 
               EventType.UPDATED.equals(this.eventType);
    }

    // Getters et Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public Transfer getTransfer() { return transfer; }
    public void setTransfer(Transfer transfer) { this.transfer = transfer; }

    public EventType getEventType() { return eventType; }
    public void setEventType(EventType eventType) { this.eventType = eventType; }

    public String getEventCode() { return eventCode; }
    public void setEventCode(String eventCode) { this.eventCode = eventCode; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getDetails() { return details; }
    public void setDetails(String details) { this.details = details; }

    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }

    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

    public String getSourceSystem() { return sourceSystem; }
    public void setSourceSystem(String sourceSystem) { this.sourceSystem = sourceSystem; }

    public String getExternalReference() { return externalReference; }
    public void setExternalReference(String externalReference) { this.externalReference = externalReference; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getUserName() { return userName; }
    public void setUserName(String userName) { this.userName = userName; }

    public String getIpAddress() { return ipAddress; }
    public void setIpAddress(String ipAddress) { this.ipAddress = ipAddress; }

    public String getUserAgent() { return userAgent; }
    public void setUserAgent(String userAgent) { this.userAgent = userAgent; }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }

    public String getCorrelationId() { return correlationId; }
    public void setCorrelationId(String correlationId) { this.correlationId = correlationId; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return "TransferEvent{" +
                "id=" + id +
                ", eventType=" + eventType +
                ", eventCode='" + eventCode + '\'' +
                ", description='" + description + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}