package com.tracker.dto;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * Data Transfer Object for category-wise normalized expense breakdowns.
 * Implements Serializable for Redis caching.
 */
public class CategoryExpenseDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    private String category;
    private long subscriptionCount;
    private BigDecimal totalMonthlyExpense;
    private BigDecimal percentageOfTotal;

    public CategoryExpenseDTO() {
    }

    public CategoryExpenseDTO(String category, long subscriptionCount, BigDecimal totalMonthlyExpense, BigDecimal percentageOfTotal) {
        this.category = category;
        this.subscriptionCount = subscriptionCount;
        this.totalMonthlyExpense = totalMonthlyExpense;
        this.percentageOfTotal = percentageOfTotal;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public long getSubscriptionCount() {
        return subscriptionCount;
    }

    public void setSubscriptionCount(long subscriptionCount) {
        this.subscriptionCount = subscriptionCount;
    }

    public BigDecimal getTotalMonthlyExpense() {
        return totalMonthlyExpense;
    }

    public void setTotalMonthlyExpense(BigDecimal totalMonthlyExpense) {
        this.totalMonthlyExpense = totalMonthlyExpense;
    }

    public BigDecimal getPercentageOfTotal() {
        return percentageOfTotal;
    }

    public void setPercentageOfTotal(BigDecimal percentageOfTotal) {
        this.percentageOfTotal = percentageOfTotal;
    }
}
