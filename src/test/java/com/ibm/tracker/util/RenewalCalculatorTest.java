package com.ibm.tracker.util;

import com.ibm.tracker.entity.BillingFrequency;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("RenewalCalculator Unit Tests - Date Arithmetic & Financial Normalization")
class RenewalCalculatorTest {

    @Test
    @DisplayName("Should advance exactly one week for WEEKLY frequency")
    void testCalculateNextRenewalDate_Weekly() {
        LocalDate start = LocalDate.of(2026, 10, 1);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.WEEKLY);
        assertEquals(LocalDate.of(2026, 10, 8), next);
    }

    @Test
    @DisplayName("Should advance exactly two weeks (14 days) for BI_WEEKLY frequency")
    void testCalculateNextRenewalDate_BiWeekly() {
        LocalDate start = LocalDate.of(2026, 10, 1);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.BI_WEEKLY);
        assertEquals(LocalDate.of(2026, 10, 15), next);
    }

    @Test
    @DisplayName("Should advance one month for standard MONTHLY frequency")
    void testCalculateNextRenewalDate_MonthlyStandard() {
        LocalDate start = LocalDate.of(2026, 5, 10);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.MONTHLY);
        assertEquals(LocalDate.of(2026, 6, 10), next);
    }

    @Test
    @DisplayName("Month-End Edge Case: Jan 31 in a non-leap year should clamp to Feb 28")
    void testCalculateNextRenewalDate_MonthEnd_NonLeapYear() {
        LocalDate start = LocalDate.of(2025, 1, 31);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.MONTHLY);
        assertEquals(LocalDate.of(2025, 2, 28), next);
    }

    @Test
    @DisplayName("Month-End Edge Case: Jan 31 in a leap year should clamp to Feb 29")
    void testCalculateNextRenewalDate_MonthEnd_LeapYear() {
        LocalDate start = LocalDate.of(2024, 1, 31);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.MONTHLY);
        assertEquals(LocalDate.of(2024, 2, 29), next);
    }

    @Test
    @DisplayName("Month-End Edge Case: Mar 31 should clamp to Apr 30 (30-day month)")
    void testCalculateNextRenewalDate_MonthEnd_ThirtyDayMonth() {
        LocalDate start = LocalDate.of(2026, 3, 31);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.MONTHLY);
        assertEquals(LocalDate.of(2026, 4, 30), next);
    }

    @Test
    @DisplayName("Quarterly calculation: Jan 31 advances 3 months and clamps to Apr 30")
    void testCalculateNextRenewalDate_Quarterly() {
        LocalDate start = LocalDate.of(2026, 1, 31);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.QUARTERLY);
        assertEquals(LocalDate.of(2026, 4, 30), next);
    }

    @Test
    @DisplayName("Semi-Annually calculation: Jan 31 advances 6 months to Jul 31")
    void testCalculateNextRenewalDate_SemiAnnually() {
        LocalDate start = LocalDate.of(2026, 1, 31);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(start, BillingFrequency.SEMI_ANNUALLY);
        assertEquals(LocalDate.of(2026, 7, 31), next);
    }

    @Test
    @DisplayName("Leap Year Edge Case: Feb 29 in leap year should project to Feb 28 in following non-leap year")
    void testCalculateNextRenewalDate_AnnuallyLeapYear() {
        LocalDate leapDay = LocalDate.of(2024, 2, 29);
        LocalDate next = RenewalCalculator.calculateNextRenewalDate(leapDay, BillingFrequency.ANNUALLY);
        assertEquals(LocalDate.of(2025, 2, 28), next);
    }

    @Test
    @DisplayName("Historical Start Date Projection: Iteratively steps forward to upcoming date on or after reference date")
    void testProjectUpcomingRenewalDate_PastDate() {
        LocalDate pastDate = LocalDate.of(2026, 1, 15);
        LocalDate reference = LocalDate.of(2026, 10, 15);

        LocalDate projected = RenewalCalculator.projectUpcomingRenewalDate(pastDate, BillingFrequency.MONTHLY, reference);
        assertEquals(LocalDate.of(2026, 10, 15), projected);

        LocalDate referenceAfter15th = LocalDate.of(2026, 10, 16);
        LocalDate nextProjected = RenewalCalculator.projectUpcomingRenewalDate(pastDate, BillingFrequency.MONTHLY, referenceAfter15th);
        assertEquals(LocalDate.of(2026, 11, 15), nextProjected);
    }

    @Test
    @DisplayName("Expense Normalization: Converts all billing cadences into exact monthly equivalents")
    void testNormalizeToMonthly() {
        // WEEKLY: 10 * 52 / 12 = 43.3333 -> 43.33
        BigDecimal weeklyNorm = RenewalCalculator.normalizeToMonthly(BigDecimal.valueOf(10.00), BillingFrequency.WEEKLY);
        assertEquals(new BigDecimal("43.33"), weeklyNorm);

        // BI_WEEKLY: 20 * 26 / 12 = 43.3333 -> 43.33
        BigDecimal biWeeklyNorm = RenewalCalculator.normalizeToMonthly(BigDecimal.valueOf(20.00), BillingFrequency.BI_WEEKLY);
        assertEquals(new BigDecimal("43.33"), biWeeklyNorm);

        // MONTHLY: 15.00 -> 15.00
        BigDecimal monthlyNorm = RenewalCalculator.normalizeToMonthly(BigDecimal.valueOf(15.00), BillingFrequency.MONTHLY);
        assertEquals(new BigDecimal("15.00"), monthlyNorm);

        // QUARTERLY: 30 / 3 = 10.00
        BigDecimal quarterlyNorm = RenewalCalculator.normalizeToMonthly(BigDecimal.valueOf(30.00), BillingFrequency.QUARTERLY);
        assertEquals(new BigDecimal("10.00"), quarterlyNorm);

        // SEMI_ANNUALLY: 60 / 6 = 10.00
        BigDecimal semiAnnualNorm = RenewalCalculator.normalizeToMonthly(BigDecimal.valueOf(60.00), BillingFrequency.SEMI_ANNUALLY);
        assertEquals(new BigDecimal("10.00"), semiAnnualNorm);

        // ANNUALLY: 120 / 12 = 10.00
        BigDecimal annualNorm = RenewalCalculator.normalizeToMonthly(BigDecimal.valueOf(120.00), BillingFrequency.ANNUALLY);
        assertEquals(new BigDecimal("10.00"), annualNorm);
    }

    @Test
    @DisplayName("Should throw IllegalArgumentException when parameters are null")
    void testNullValidation() {
        assertThrows(IllegalArgumentException.class, () -> RenewalCalculator.calculateNextRenewalDate(null, BillingFrequency.MONTHLY));
        assertThrows(IllegalArgumentException.class, () -> RenewalCalculator.calculateNextRenewalDate(LocalDate.now(), null));
        assertThrows(IllegalArgumentException.class, () -> RenewalCalculator.normalizeToMonthly(null, BillingFrequency.MONTHLY));
    }
}
