package com.tracker.service.impl;

import com.tracker.dto.CategoryExpenseDTO;
import com.tracker.dto.MonthlyExpenseSummaryDTO;
import com.tracker.entity.Subscription;
import com.tracker.entity.SubscriptionStatus;
import com.tracker.repository.SubscriptionRepository;
import com.tracker.service.ExpenseService;
import com.tracker.util.RenewalCalculator;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Production implementation of ExpenseService.
 * Computes normalized recurring spending metrics and category breakdowns with Redis caching.
 */
@Service
public class ExpenseServiceImpl implements ExpenseService {

    private final SubscriptionRepository subscriptionRepository;

    public ExpenseServiceImpl(SubscriptionRepository subscriptionRepository) {
        this.subscriptionRepository = subscriptionRepository;
    }

    @Override
    @Transactional(readOnly = true)
    @Cacheable(value = "monthlySummary", key = "'summary'")
    public MonthlyExpenseSummaryDTO getExpenseSummary() {
        List<Subscription> activeSubscriptions = subscriptionRepository.findByStatus(SubscriptionStatus.ACTIVE);

        if (activeSubscriptions.isEmpty()) {
            return new MonthlyExpenseSummaryDTO(
                    0,
                    BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP),
                    BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP),
                    "USD",
                    LocalDateTime.now()
            );
        }

        BigDecimal totalMonthly = BigDecimal.ZERO;
        for (Subscription sub : activeSubscriptions) {
            BigDecimal monthly = RenewalCalculator.normalizeToMonthly(sub.getAmount(), sub.getBillingFrequency());
            totalMonthly = totalMonthly.add(monthly);
        }

        BigDecimal totalAnnual = totalMonthly.multiply(BigDecimal.valueOf(12)).setScale(2, RoundingMode.HALF_UP);

        return new MonthlyExpenseSummaryDTO(
                activeSubscriptions.size(),
                totalMonthly.setScale(2, RoundingMode.HALF_UP),
                totalAnnual,
                "USD",
                LocalDateTime.now()
        );
    }

    @Override
    @Transactional(readOnly = true)
    @Cacheable(value = "categorySummary", key = "'byCategory'")
    public List<CategoryExpenseDTO> getExpensesByCategory() {
        List<Subscription> activeSubscriptions = subscriptionRepository.findByStatus(SubscriptionStatus.ACTIVE);

        if (activeSubscriptions.isEmpty()) {
            return Collections.emptyList();
        }

        // Group active subscriptions by category
        Map<String, List<Subscription>> groupedByCategory = activeSubscriptions.stream()
                .collect(Collectors.groupingBy(s -> s.getCategory().toUpperCase()));

        // Calculate total monthly expenditure across all categories
        BigDecimal overallTotalMonthly = BigDecimal.ZERO;
        Map<String, BigDecimal> categoryTotals = new HashMap<>();

        for (Map.Entry<String, List<Subscription>> entry : groupedByCategory.entrySet()) {
            BigDecimal categoryTotal = BigDecimal.ZERO;
            for (Subscription sub : entry.getValue()) {
                categoryTotal = categoryTotal.add(RenewalCalculator.normalizeToMonthly(sub.getAmount(), sub.getBillingFrequency()));
            }
            categoryTotals.put(entry.getKey(), categoryTotal);
            overallTotalMonthly = overallTotalMonthly.add(categoryTotal);
        }

        List<CategoryExpenseDTO> result = new ArrayList<>();
        final BigDecimal totalExpenseForPercentage = overallTotalMonthly;

        for (Map.Entry<String, List<Subscription>> entry : groupedByCategory.entrySet()) {
            String category = entry.getKey();
            long count = entry.getValue().size();
            BigDecimal catTotal = categoryTotals.get(category).setScale(2, RoundingMode.HALF_UP);

            BigDecimal percentage;
            if (totalExpenseForPercentage.compareTo(BigDecimal.ZERO) > 0) {
                percentage = catTotal.multiply(BigDecimal.valueOf(100))
                        .divide(totalExpenseForPercentage, 2, RoundingMode.HALF_UP);
            } else {
                percentage = BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP);
            }

            result.add(new CategoryExpenseDTO(category, count, catTotal, percentage));
        }

        // Sort descending by monthly expense
        result.sort((a, b) -> b.getTotalMonthlyExpense().compareTo(a.getTotalMonthlyExpense()));
        return result;
    }
}
