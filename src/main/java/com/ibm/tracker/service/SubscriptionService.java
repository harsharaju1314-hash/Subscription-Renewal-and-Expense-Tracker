package com.ibm.tracker.service;

import com.ibm.tracker.dto.PagedResponseDTO;
import com.ibm.tracker.dto.SubscriptionRequestDTO;
import com.ibm.tracker.dto.SubscriptionResponseDTO;

import java.util.List;

/**
 * Service interface defining subscription management lifecycle operations.
 */
public interface SubscriptionService {

    /**
     * Creates a new subscription, computes its initial next renewal date, and clears cached summaries.
     */
    SubscriptionResponseDTO createSubscription(SubscriptionRequestDTO request);

    /**
     * Retrieves paginated, sorted, and optionally filtered subscriptions.
     */
    PagedResponseDTO<SubscriptionResponseDTO> getAllSubscriptions(String category, String status, int page, int size, String sortBy, String sortDir);

    /**
     * Retrieves a single subscription by unique identifier.
     */
    SubscriptionResponseDTO getSubscriptionById(Long id);

    /**
     * Updates subscription fields, recalculates renewal if cadence/start date changed, and evicts cache.
     */
    SubscriptionResponseDTO updateSubscription(Long id, SubscriptionRequestDTO request);

    /**
     * Deletes a subscription and evicts cache.
     */
    void deleteSubscription(Long id);

    /**
     * Returns subscriptions renewing within the next N days (cached in Redis).
     */
    List<SubscriptionResponseDTO> getUpcomingRenewals(int days);
}
