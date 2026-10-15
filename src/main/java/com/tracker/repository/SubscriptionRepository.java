package com.tracker.repository;

import com.tracker.entity.Subscription;
import com.tracker.entity.SubscriptionStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Spring Data JPA repository for the Subscription entity.
 * Provides custom queries optimized with database indexes for upcoming renewals and category breakdowns.
 */
@Repository
public interface SubscriptionRepository extends JpaRepository<Subscription, Long> {

    /**
     * Finds subscriptions by status with pagination and sorting.
     */
    Page<Subscription> findByStatus(SubscriptionStatus status, Pageable pageable);

    /**
     * Finds subscriptions by category and status with pagination.
     */
    Page<Subscription> findByCategoryIgnoreCaseAndStatus(String category, SubscriptionStatus status, Pageable pageable);

    /**
     * Finds subscriptions by category (regardless of status).
     */
    Page<Subscription> findByCategoryIgnoreCase(String category, Pageable pageable);

    /**
     * Fetches active subscriptions whose next renewal falls within the specified date window.
     * Utilizes the composite index (next_renewal_date, status).
     */
    @Query("SELECT s FROM Subscription s WHERE s.status = :status " +
           "AND s.nextRenewalDate BETWEEN :startDate AND :endDate " +
           "ORDER BY s.nextRenewalDate ASC")
    List<Subscription> findUpcomingRenewals(
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate,
            @Param("status") SubscriptionStatus status
    );

    /**
     * Retrieves all subscriptions by status for aggregation math.
     */
    List<Subscription> findByStatus(SubscriptionStatus status);

    /**
     * Retrieves distinct categories present in active subscriptions.
     */
    @Query("SELECT DISTINCT s.category FROM Subscription s WHERE s.status = :status ORDER BY s.category ASC")
    List<String> findDistinctCategoriesByStatus(@Param("status") SubscriptionStatus status);

    /**
     * Counts active subscriptions.
     */
    long countByStatus(SubscriptionStatus status);
}
