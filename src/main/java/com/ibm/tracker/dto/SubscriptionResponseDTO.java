package com.ibm.tracker.dto;

import com.ibm.tracker.entity.BillingFrequency;
import com.ibm.tracker.entity.SubscriptionStatus;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Data Transfer Object returned from the API representing a subscription record.
 * Implements Serializable for Redis caching compatibility.
 */
public class SubscriptionResponseDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long id;
    private String name;
    private String category;
    private BigDecimal amount;
    private String currency;
    private BillingFrequency billingFrequency;
    private LocalDate startDate;
    private LocalDate nextRenewalDate;
    private SubscriptionStatus status;
    private LocalDate cancellationDate;
    private String notes;
    private BigDecimal monthlyEquivalentAmount;
    private long daysUntilRenewal;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public SubscriptionResponseDTO() {
    }

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

    public BigDecimal getMonthlyEquivalentAmount() {
        return monthlyEquivalentAmount;
    }

    public void setMonthlyEquivalentAmount(BigDecimal monthlyEquivalentAmount) {
        this.monthlyEquivalentAmount = monthlyEquivalentAmount;
    }

    public long getDaysUntilRenewal() {
        return daysUntilRenewal;
    }

    public void setDaysUntilRenewal(long daysUntilRenewal) {
        this.daysUntilRenewal = daysUntilRenewal;
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
