package com.tracker.dto;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Data Transfer Object containing portfolio-wide aggregated recurring expense metrics.
 * Implements Serializable for Redis caching.
 */
public class MonthlyExpenseSummaryDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    private long totalActiveSubscriptions;
    private BigDecimal totalMonthlyExpense;
    private BigDecimal totalAnnualExpense;
    private String currency;
    private LocalDateTime calculatedAt;

    public MonthlyExpenseSummaryDTO() {
    }

    public MonthlyExpenseSummaryDTO(long totalActiveSubscriptions, BigDecimal totalMonthlyExpense,
                                   BigDecimal totalAnnualExpense, String currency, LocalDateTime calculatedAt) {
        this.totalActiveSubscriptions = totalActiveSubscriptions;
        this.totalMonthlyExpense = totalMonthlyExpense;
        this.totalAnnualExpense = totalAnnualExpense;
        this.currency = currency;
        this.calculatedAt = calculatedAt;
    }

    public long getTotalActiveSubscriptions() {
        return totalActiveSubscriptions;
    }

    public void setTotalActiveSubscriptions(long totalActiveSubscriptions) {
        this.totalActiveSubscriptions = totalActiveSubscriptions;
    }

    public BigDecimal getTotalMonthlyExpense() {
        return totalMonthlyExpense;
    }

    public void setTotalMonthlyExpense(BigDecimal totalMonthlyExpense) {
        this.totalMonthlyExpense = totalMonthlyExpense;
    }

    public BigDecimal getTotalAnnualExpense() {
        return totalAnnualExpense;
    }

    public void setTotalAnnualExpense(BigDecimal totalAnnualExpense) {
        this.totalAnnualExpense = totalAnnualExpense;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public LocalDateTime getCalculatedAt() {
        return calculatedAt;
    }

    public void setCalculatedAt(LocalDateTime calculatedAt) {
        this.calculatedAt = calculatedAt;
    }
}
