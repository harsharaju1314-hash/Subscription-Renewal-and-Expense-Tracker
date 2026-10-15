package com.tracker.util;

import com.tracker.entity.BillingFrequency;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.Year;

/**
 * Pure domain utility for deterministic renewal date projections and normalized financial arithmetic.
 * 
 * CALCULATION ASSUMPTIONS & DESIGN DECISIONS:
 * 1. Base Dates: Next renewal date is projected by adding the interval to the anchor date.
 * 2. Month-End Clamping: For MONTHLY, QUARTERLY, and SEMI_ANNUALLY cadences, java.time.LocalDate.plusMonths()
 *    automatically clamps dates exceeding target month length to the last valid day of that month
 *    (e.g., Jan 31 -> Feb 28 in a non-leap year, or Feb 29 in a leap year).
 * 3. Leap Year Handling: For ANNUALLY subscriptions starting on Feb 29 (leap year), plusYears(1)
 *    resolves deterministically to Feb 28 of the following non-leap year.
 * 4. Past Dates: When computing next upcoming renewal from a historical start date relative to today,
 *    intervals are advanced repeatedly until the renewal date is strictly >= the reference date.
 * 5. Monetary Arithmetic: All normalized expense math uses BigDecimal with 4 internal decimal places
 *    and RoundingMode.HALF_UP, rounded to 2 decimal places for user-facing outputs.
 */
public final class RenewalCalculator {

    private RenewalCalculator() {
        // Prevent instantiation
    }

    /**
     * Calculates the immediate next renewal date given a base date and frequency.
     *
     * @param baseDate  Anchor date from which to advance
     * @param frequency Billing cadence
     * @return Projected next renewal date
     */
    public static LocalDate calculateNextRenewalDate(LocalDate baseDate, BillingFrequency frequency) {
        if (baseDate == null) {
            throw new IllegalArgumentException("Base date cannot be null");
        }
        if (frequency == null) {
            throw new IllegalArgumentException("Billing frequency cannot be null");
        }

        return switch (frequency) {
            case WEEKLY -> baseDate.plusWeeks(1);
            case BI_WEEKLY -> baseDate.plusWeeks(2);
            case MONTHLY -> baseDate.plusMonths(1);
            case QUARTERLY -> baseDate.plusMonths(3);
            case SEMI_ANNUALLY -> baseDate.plusMonths(6);
            case ANNUALLY -> baseDate.plusYears(1);
        };
    }

    /**
     * Projects the earliest renewal date that falls on or after the specified reference date.
     * If the baseDate is already in the future or equal to referenceDate, baseDate is returned.
     * Otherwise, steps forward iteratively according to the frequency.
     *
     * @param startDate     Original subscription start date
     * @param frequency     Billing cadence
     * @param referenceDate Point in time to project against (typically LocalDate.now())
     * @return Projected upcoming renewal date >= referenceDate
     */
    public static LocalDate projectUpcomingRenewalDate(LocalDate startDate, BillingFrequency frequency, LocalDate referenceDate) {
        if (startDate == null || referenceDate == null) {
            throw new IllegalArgumentException("Dates cannot be null");
        }
        if (frequency == null) {
            throw new IllegalArgumentException("Billing frequency cannot be null");
        }

        if (!startDate.isBefore(referenceDate)) {
            return startDate;
        }

        LocalDate current = startDate;
        while (current.isBefore(referenceDate)) {
            current = calculateNextRenewalDate(current, frequency);
        }
        return current;
    }

    /**
     * Converts any subscription amount to an exact monthly normalized cost.
     * Formulas:
     * - WEEKLY: amount * 52 / 12
     * - BI_WEEKLY: amount * 26 / 12
     * - MONTHLY: amount
     * - QUARTERLY: amount / 3
     * - SEMI_ANNUALLY: amount / 6
     * - ANNUALLY: amount / 12
     *
     * @param amount    Subscription cost
     * @param frequency Billing cadence
     * @return Normalized monthly expenditure (rounded to 2 decimal places)
     */
    public static BigDecimal normalizeToMonthly(BigDecimal amount, BillingFrequency frequency) {
        if (amount == null) {
            throw new IllegalArgumentException("Amount cannot be null");
        }
        if (frequency == null) {
            throw new IllegalArgumentException("Billing frequency cannot be null");
        }

        return switch (frequency) {
            case WEEKLY -> amount.multiply(BigDecimal.valueOf(52))
                    .divide(BigDecimal.valueOf(12), 4, RoundingMode.HALF_UP)
                    .setScale(2, RoundingMode.HALF_UP);
            case BI_WEEKLY -> amount.multiply(BigDecimal.valueOf(26))
                    .divide(BigDecimal.valueOf(12), 4, RoundingMode.HALF_UP)
                    .setScale(2, RoundingMode.HALF_UP);
            case MONTHLY -> amount.setScale(2, RoundingMode.HALF_UP);
            case QUARTERLY -> amount.divide(BigDecimal.valueOf(3), 4, RoundingMode.HALF_UP)
                    .setScale(2, RoundingMode.HALF_UP);
            case SEMI_ANNUALLY -> amount.divide(BigDecimal.valueOf(6), 4, RoundingMode.HALF_UP)
                    .setScale(2, RoundingMode.HALF_UP);
            case ANNUALLY -> amount.divide(BigDecimal.valueOf(12), 4, RoundingMode.HALF_UP)
                    .setScale(2, RoundingMode.HALF_UP);
        };
    }

    /**
     * Helper to verify if a given year is a leap year.
     */
    public static boolean isLeapYear(int year) {
        return Year.of(year).isLeap();
    }
}
