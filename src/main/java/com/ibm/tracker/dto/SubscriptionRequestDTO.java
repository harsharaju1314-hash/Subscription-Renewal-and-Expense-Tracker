package com.ibm.tracker.dto;

import com.ibm.tracker.entity.BillingFrequency;
import com.ibm.tracker.entity.SubscriptionStatus;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Data Transfer Object for creating or updating a subscription.
 * Encapsulates client input and enforces declarative validation rules.
 */
public class SubscriptionRequestDTO {

    @NotBlank(message = "Subscription name is required")
    @Size(max = 100, message = "Subscription name must not exceed 100 characters")
    private String name;

    @NotBlank(message = "Category is required")
    @Size(max = 50, message = "Category must not exceed 50 characters")
    private String category;

    @NotNull(message = "Amount is required")
    @Positive(message = "Amount must be strictly greater than 0")
    @Digits(integer = 8, fraction = 2, message = "Amount must have at most 2 decimal places")
    private BigDecimal amount;

    @Pattern(regexp = "^[A-Za-z]{3}$", message = "Currency must be a 3-letter ISO code (e.g., USD, EUR)")
    private String currency = "USD";

    @NotNull(message = "Billing frequency is required")
    private BillingFrequency billingFrequency;

    @NotNull(message = "Start date is required")
    private LocalDate startDate;

    private SubscriptionStatus status = SubscriptionStatus.ACTIVE;

    @Size(max = 255, message = "Notes must not exceed 255 characters")
    private String notes;

    public SubscriptionRequestDTO() {
    }

    public SubscriptionRequestDTO(String name, String category, BigDecimal amount, String currency,
                                  BillingFrequency billingFrequency, LocalDate startDate,
                                  SubscriptionStatus status, String notes) {
        this.name = name;
        this.category = category;
        this.amount = amount;
        this.currency = currency;
        this.billingFrequency = billingFrequency;
        this.startDate = startDate;
        this.status = status;
        this.notes = notes;
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

    public SubscriptionStatus getStatus() {
        return status;
    }

    public void setStatus(SubscriptionStatus status) {
        this.status = status;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }
}
