package com.tracker.service;

import com.tracker.dto.CategoryExpenseDTO;
import com.tracker.dto.MonthlyExpenseSummaryDTO;

import java.util.List;

/**
 * Service interface for recurring expense aggregation and financial analytics.
 */
public interface ExpenseService {

    /**
     * Calculates the aggregate portfolio spend normalized across all active subscriptions.
     * Cached in Redis.
     */
    MonthlyExpenseSummaryDTO getExpenseSummary();

    /**
     * Groups normalized monthly spending by category and calculates percentage shares.
     * Cached in Redis.
     */
    List<CategoryExpenseDTO> getExpensesByCategory();
}
