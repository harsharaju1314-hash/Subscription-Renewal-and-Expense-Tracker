package com.tracker.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * JPA Entity mapping to the 'subscriptions' table.
 * Demonstrates relational modeling, auditing hooks, and domain constraints.
 */
@Entity
@Table(
    name = "subscriptions",
    indexes = {
        @Index(name = "idx_sub_renewal_status", columnList = "next_renewal_date, status"),
        @Index(name = "idx_sub_category_status", columnList = "category, status"),
        @Index(name = "idx_sub_status", columnList = "status")
    }
)
public class Subscription {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "category", nullable = false, length = 50)
    private String category;

    @Column(name = "amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Column(name = "currency", nullable = false, length = 3)
    private String currency = "USD";

    @Enumerated(EnumType.STRING)
    @Column(name = "billing_frequency", nullable = false, length = 20)
    private BillingFrequency billingFrequency;

    @Column(name = "start_date", nullable = false)
    private LocalDate startDate;

    @Column(name = "next_renewal_date", nullable = false)
    private LocalDate nextRenewalDate;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private SubscriptionStatus status = SubscriptionStatus.ACTIVE;

    @Column(name = "cancellation_date")
    private LocalDate cancellationDate;

    @Column(name = "notes", length = 255)
    private String notes;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    public Subscription() {
    }

    public Subscription(Long id, String name, String category, BigDecimal amount, String currency,
                        BillingFrequency billingFrequency, LocalDate startDate, LocalDate nextRenewalDate,
                        SubscriptionStatus status, LocalDate cancellationDate, String notes) {
        this.id = id;
        this.name = name;
        this.category = category;
        this.amount = amount;
        this.currency = (currency != null && !currency.isBlank()) ? currency.toUpperCase() : "USD";
        this.billingFrequency = billingFrequency;
        this.startDate = startDate;
        this.nextRenewalDate = nextRenewalDate;
        this.status = (status != null) ? status : SubscriptionStatus.ACTIVE;
        this.cancellationDate = cancellationDate;
        this.notes = notes;
    }

    @PrePersist
    protected void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        this.createdAt = now;
        this.updatedAt = now;
        if (this.currency == null || this.currency.isBlank()) {
            this.currency = "USD";
        }
        if (this.status == null) {
            this.status = SubscriptionStatus.ACTIVE;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public BillingFrequency getBillingFrequency() {
        return billingFrequency;
    }

    public void setBillingFrequency(BillingFrequency billingFrequency) {
        this.billingFrequency = billingFrequency;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public void setStartDate(LocalDate startDate) {
        this.startDate = startDate;
    }

    public LocalDate getNextRenewalDate() {
        return nextRenewalDate;
    }

    public void setNextRenewalDate(LocalDate nextRenewalDate) {
        this.nextRenewalDate = nextRenewalDate;
    }

    public SubscriptionStatus getStatus() {
        return status;
    }

    public void setStatus(SubscriptionStatus status) {
        this.status = status;
    }

    public LocalDate getCancellationDate() {
        return cancellationDate;
    }

    public void setCancellationDate(LocalDate cancellationDate) {
        this.cancellationDate = cancellationDate;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}
