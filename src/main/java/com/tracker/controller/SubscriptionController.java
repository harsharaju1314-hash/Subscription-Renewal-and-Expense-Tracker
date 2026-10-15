package com.tracker.controller;

import com.tracker.dto.PagedResponseDTO;
import com.tracker.dto.SubscriptionRequestDTO;
import com.tracker.dto.SubscriptionResponseDTO;
import com.tracker.service.SubscriptionService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller exposing subscription management endpoints (Endpoints 1 to 6).
 */
@RestController
@RequestMapping("/api/v1/subscriptions")
@CrossOrigin(origins = "*") // Allows flexible integration across local frontends
public class SubscriptionController {

    private final SubscriptionService subscriptionService;

    public SubscriptionController(SubscriptionService subscriptionService) {
        this.subscriptionService = subscriptionService;
    }

    /**
     * Endpoint 1: Create a new subscription.
     * HTTP 201 Created on success; HTTP 400 on validation error.
     */
    @PostMapping
    public ResponseEntity<SubscriptionResponseDTO> createSubscription(@Valid @RequestBody SubscriptionRequestDTO request) {
        SubscriptionResponseDTO created = subscriptionService.createSubscription(request);
        return new ResponseEntity<>(created, HttpStatus.CREATED);
    }

    /**
     * Endpoint 2: Retrieve paginated subscriptions with optional category and status filtering.
     * HTTP 200 OK.
     */
    @GetMapping
    public ResponseEntity<PagedResponseDTO<SubscriptionResponseDTO>> getAllSubscriptions(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "nextRenewalDate") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir
    ) {
        PagedResponseDTO<SubscriptionResponseDTO> response = subscriptionService.getAllSubscriptions(
                category, status, page, size, sortBy, sortDir
        );
        return ResponseEntity.ok(response);
    }

    /**
     * Endpoint 3: Retrieve a single subscription by ID.
     * HTTP 200 OK on success; HTTP 404 if not found.
     */
    @GetMapping("/{id}")
    public ResponseEntity<SubscriptionResponseDTO> getSubscriptionById(@PathVariable Long id) {
        SubscriptionResponseDTO subscription = subscriptionService.getSubscriptionById(id);
        return ResponseEntity.ok(subscription);
    }

    /**
     * Endpoint 4: Update an existing subscription by ID.
     * HTTP 200 OK on success; HTTP 400 on validation error; HTTP 404 if not found.
     */
    @PutMapping("/{id}")
    public ResponseEntity<SubscriptionResponseDTO> updateSubscription(
            @PathVariable Long id,
            @Valid @RequestBody SubscriptionRequestDTO request
    ) {
        SubscriptionResponseDTO updated = subscriptionService.updateSubscription(id, request);
        return ResponseEntity.ok(updated);
    }

    /**
     * Endpoint 5: Delete a subscription by ID.
     * HTTP 204 No Content on success; HTTP 404 if not found.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSubscription(@PathVariable Long id) {
        subscriptionService.deleteSubscription(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Endpoint 6: Fetch upcoming renewals within next N days.
     * HTTP 200 OK. Cached in Redis.
     */
    @GetMapping("/upcoming")
    public ResponseEntity<List<SubscriptionResponseDTO>> getUpcomingRenewals(
            @RequestParam(defaultValue = "30") int days
    ) {
        List<SubscriptionResponseDTO> renewals = subscriptionService.getUpcomingRenewals(days);
        return ResponseEntity.ok(renewals);
    }
}
