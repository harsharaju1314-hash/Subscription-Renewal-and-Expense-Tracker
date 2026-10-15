package com.tracker.service;

import com.tracker.dto.CategoryExpenseDTO;
import com.tracker.dto.MonthlyExpenseSummaryDTO;
import com.tracker.entity.BillingFrequency;
import com.tracker.entity.Subscription;
import com.tracker.entity.SubscriptionStatus;
import com.tracker.repository.SubscriptionRepository;
import com.tracker.service.impl.ExpenseServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@DisplayName("ExpenseService Unit Tests - Normalization & Category Breakdowns")
class ExpenseServiceTest {

    @Mock
    private SubscriptionRepository subscriptionRepository;

    @InjectMocks
    private ExpenseServiceImpl expenseService;

    private Subscription subMonthly;
    private Subscription subAnnual;

    @BeforeEach
    void setUp() {
        // Netflix: $15.00 / month = $15.00 / month
        subMonthly = new Subscription(
                1L, "Netflix", "STREAMING", BigDecimal.valueOf(15.00), "USD",
                BillingFrequency.MONTHLY, LocalDate.of(2026, 1, 1), LocalDate.of(2026, 11, 1),
                SubscriptionStatus.ACTIVE, null, "Streaming"
        );

        // JetBrains: $120.00 / year = $10.00 / month
        subAnnual = new Subscription(
                2L, "JetBrains", "SOFTWARE", BigDecimal.valueOf(120.00), "USD",
                BillingFrequency.ANNUALLY, LocalDate.of(2026, 1, 1), LocalDate.of(2027, 1, 1),
                SubscriptionStatus.ACTIVE, null, "IDE"
        );
    }

    @Test
    @DisplayName("getExpenseSummary: Should calculate normalized monthly & annual expenditure")
    void testGetExpenseSummary_WithActiveSubscriptions() {
        when(subscriptionRepository.findByStatus(SubscriptionStatus.ACTIVE))
                .thenReturn(Arrays.asList(subMonthly, subAnnual));

        MonthlyExpenseSummaryDTO summary = expenseService.getExpenseSummary();

        assertNotNull(summary);
        assertEquals(2, summary.getTotalActiveSubscriptions());
        // Monthly: $15.00 + $10.00 = $25.00
        assertEquals(new BigDecimal("25.00"), summary.getTotalMonthlyExpense());
        // Annual: $25.00 * 12 = $300.00
        assertEquals(new BigDecimal("300.00"), summary.getTotalAnnualExpense());
    }

    @Test
    @DisplayName("getExpenseSummary: Should return zero totals when no active subscriptions exist")
    void testGetExpenseSummary_Empty() {
        when(subscriptionRepository.findByStatus(SubscriptionStatus.ACTIVE))
                .thenReturn(Collections.emptyList());

        MonthlyExpenseSummaryDTO summary = expenseService.getExpenseSummary();

        assertNotNull(summary);
        assertEquals(0, summary.getTotalActiveSubscriptions());
        assertEquals(new BigDecimal("0.00"), summary.getTotalMonthlyExpense());
        assertEquals(new BigDecimal("0.00"), summary.getTotalAnnualExpense());
    }

    @Test
    @DisplayName("getExpensesByCategory: Should group by category and compute percentage of total")
    void testGetExpensesByCategory() {
        when(subscriptionRepository.findByStatus(SubscriptionStatus.ACTIVE))
                .thenReturn(Arrays.asList(subMonthly, subAnnual));

        List<CategoryExpenseDTO> categories = expenseService.getExpensesByCategory();

        assertNotNull(categories);
        assertEquals(2, categories.size());

        // STREAMING is $15.00 out of $25.00 = 60.00%
        CategoryExpenseDTO streaming = categories.stream()
                .filter(c -> "STREAMING".equals(c.getCategory()))
                .findFirst()
                .orElse(null);
        assertNotNull(streaming);
        assertEquals(1, streaming.getSubscriptionCount());
        assertEquals(new BigDecimal("15.00"), streaming.getTotalMonthlyExpense());
        assertEquals(new BigDecimal("60.00"), streaming.getPercentageOfTotal());

        // SOFTWARE is $10.00 out of $25.00 = 40.00%
        CategoryExpenseDTO software = categories.stream()
                .filter(c -> "SOFTWARE".equals(c.getCategory()))
                .findFirst()
                .orElse(null);
        assertNotNull(software);
        assertEquals(1, software.getSubscriptionCount());
        assertEquals(new BigDecimal("10.00"), software.getTotalMonthlyExpense());
        assertEquals(new BigDecimal("40.00"), software.getPercentageOfTotal());
    }
}
