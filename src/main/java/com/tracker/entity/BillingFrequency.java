package com.tracker.entity;

/**
 * Supported subscription billing frequencies with human-readable labels.
 */
public enum BillingFrequency {
    WEEKLY("Weekly"),
    BI_WEEKLY("Bi-Weekly"),
    MONTHLY("Monthly"),
    QUARTERLY("Quarterly"),
    SEMI_ANNUALLY("Semi-Annually"),
    ANNUALLY("Annually");

    private final String displayName;

    BillingFrequency(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }

    public static boolean isValid(String value) {
        if (value == null) return false;
        try {
            BillingFrequency.valueOf(value.toUpperCase());
            return true;
        } catch (IllegalArgumentException e) {
            return false;
        }
    }
}
