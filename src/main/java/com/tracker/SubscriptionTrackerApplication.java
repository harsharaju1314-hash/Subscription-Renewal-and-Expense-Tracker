package com.tracker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

/**
 * Entry point for the Subscription Renewal and Expense Tracker application.
 * Enables Spring Caching support with Redis integration.
 */
@SpringBootApplication
@EnableCaching
public class SubscriptionTrackerApplication {

    public static void main(String[] args) {
        SpringApplication.run(SubscriptionTrackerApplication.class, args);
    }
}
