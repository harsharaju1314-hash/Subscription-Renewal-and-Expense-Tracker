package com.ibm.tracker.service.impl;

import com.ibm.tracker.dto.PagedResponseDTO;
import com.ibm.tracker.dto.SubscriptionRequestDTO;
import com.ibm.tracker.dto.SubscriptionResponseDTO;
import com.ibm.tracker.entity.BillingFrequency;
import com.ibm.tracker.entity.Subscription;
import com.ibm.tracker.entity.SubscriptionStatus;
import com.ibm.tracker.exception.ResourceNotFoundException;
import com.ibm.tracker.repository.SubscriptionRepository;
import com.ibm.tracker.service.SubscriptionService;
import com.ibm.tracker.util.RenewalCalculator;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Production implementation of SubscriptionService.
 * Coordinates persistence, renewal arithmetic, and cache eviction across write operations.
 */
@Service
public class SubscriptionServiceImpl implements SubscriptionService {

    private final SubscriptionRepository subscriptionRepository;

    public SubscriptionServiceImpl(SubscriptionRepository subscriptionRepository) {
        this.subscriptionRepository = subscriptionRepository;
    }

    @Override
    @Transactional
    @CacheEvict(value = {"monthlySummary", "categorySummary", "upcomingRenewals"}, allEntries = true)
    public SubscriptionResponseDTO createSubscription(SubscriptionRequestDTO request) {
        Subscription subscription = new Subscription();
        subscription.setName(request.getName().trim());
        subscription.setCategory(request.getCategory().trim().toUpperCase());
        subscription.setAmount(request.getAmount().setScale(2, java.math.RoundingMode.HALF_UP));
        subscription.setCurrency(request.getCurrency() != null ? request.getCurrency().trim().toUpperCase() : "USD");
        subscription.setBillingFrequency(request.getBillingFrequency());
        subscription.setStartDate(request.getStartDate());
        subscription.setStatus(request.getStatus() != null ? request.getStatus() : SubscriptionStatus.ACTIVE);
        subscription.setNotes(request.getNotes());

        // Calculate next renewal date based on start date and frequency
        LocalDate today = LocalDate.now();
        LocalDate calculatedRenewal;
        if (request.getStartDate().isAfter(today)) {
            calculatedRenewal = RenewalCalculator.calculateNextRenewalDate(request.getStartDate(), request.getBillingFrequency());
        } else {
            calculatedRenewal = RenewalCalculator.projectUpcomingRenewalDate(request.getStartDate(), request.getBillingFrequency(), today);
        }
        subscription.setNextRenewalDate(calculatedRenewal);

        Subscription saved = subscriptionRepository.save(subscription);
        return mapToDTO(saved);
    }

    @Override
    @Transactional(readOnly = true)
    public PagedResponseDTO<SubscriptionResponseDTO> getAllSubscriptions(String category, String status, int page, int size, String sortBy, String sortDir) {
        // Enforce pagination bounds
        int validatedPage = Math.max(page, 0);
        int validatedSize = (size > 0 && size <= 100) ? size : 10;

        // Default sort validation
        String validatedSortBy = (sortBy != null && !sortBy.isBlank()) ? sortBy : "nextRenewalDate";
        Sort.Direction direction = "desc".equalsIgnoreCase(sortDir) ? Sort.Direction.DESC : Sort.Direction.ASC;
        Pageable pageable = PageRequest.of(validatedPage, validatedSize, Sort.by(direction, validatedSortBy));

        Page<Subscription> subscriptionPage;

        SubscriptionStatus filterStatus = null;
        if (status != null && !status.isBlank() && !"ALL".equalsIgnoreCase(status)) {
            try {
                filterStatus = SubscriptionStatus.valueOf(status.trim().toUpperCase());
            } catch (IllegalArgumentException ignored) {
                // Ignore invalid status filter, defaults to all
            }
        }

        boolean hasCategory = category != null && !category.isBlank() && !"ALL".equalsIgnoreCase(category);

        if (hasCategory && filterStatus != null) {
            subscriptionPage = subscriptionRepository.findByCategoryIgnoreCaseAndStatus(category.trim(), filterStatus, pageable);
        } else if (hasCategory) {
            subscriptionPage = subscriptionRepository.findByCategoryIgnoreCase(category.trim(), pageable);
        } else if (filterStatus != null) {
            subscriptionPage = subscriptionRepository.findByStatus(filterStatus, pageable);
        } else {
            subscriptionPage = subscriptionRepository.findAll(pageable);
        }

        List<SubscriptionResponseDTO> dtoList = subscriptionPage.getContent()
                .stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());

        return new PagedResponseDTO<>(
                dtoList,
                subscriptionPage.getNumber(),
                subscriptionPage.getSize(),
                subscriptionPage.getTotalElements(),
                subscriptionPage.getTotalPages(),
                subscriptionPage.isLast(),
                subscriptionPage.isFirst()
        );
    }

    @Override
    @Transactional(readOnly = true)
    public SubscriptionResponseDTO getSubscriptionById(Long id) {
        Subscription subscription = subscriptionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Subscription", "id", id));
        return mapToDTO(subscription);
    }

    @Override
    @Transactional
    @CacheEvict(value = {"monthlySummary", "categorySummary", "upcomingRenewals"}, allEntries = true)
    public SubscriptionResponseDTO updateSubscription(Long id, SubscriptionRequestDTO request) {
        Subscription subscription = subscriptionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Subscription", "id", id));

        subscription.setName(request.getName().trim());
        subscription.setCategory(request.getCategory().trim().toUpperCase());
        subscription.setAmount(request.getAmount().setScale(2, java.math.RoundingMode.HALF_UP));
        if (request.getCurrency() != null && !request.getCurrency().isBlank()) {
            subscription.setCurrency(request.getCurrency().trim().toUpperCase());
        }

        boolean cadenceOrStartChanged = !subscription.getBillingFrequency().equals(request.getBillingFrequency())
                || !subscription.getStartDate().isEqual(request.getStartDate());

        subscription.setBillingFrequency(request.getBillingFrequency());
        subscription.setStartDate(request.getStartDate());

        if (request.getStatus() != null) {
            subscription.setStatus(request.getStatus());
            if (request.getStatus() == SubscriptionStatus.CANCELLED && subscription.getCancellationDate() == null) {
                subscription.setCancellationDate(LocalDate.now());
            } else if (request.getStatus() == SubscriptionStatus.ACTIVE) {
                subscription.setCancellationDate(null);
            }
        }

        subscription.setNotes(request.getNotes());

        if (cadenceOrStartChanged) {
            LocalDate today = LocalDate.now();
            LocalDate newRenewal = RenewalCalculator.projectUpcomingRenewalDate(request.getStartDate(), request.getBillingFrequency(), today);
            subscription.setNextRenewalDate(newRenewal);
        }

        Subscription updated = subscriptionRepository.save(subscription);
        return mapToDTO(updated);
    }

    @Override
    @Transactional
    @CacheEvict(value = {"monthlySummary", "categorySummary", "upcomingRenewals"}, allEntries = true)
    public void deleteSubscription(Long id) {
        Subscription subscription = subscriptionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Subscription", "id", id));
        subscriptionRepository.delete(subscription);
    }

    @Override
    @Transactional(readOnly = true)
    @Cacheable(value = "upcomingRenewals", key = "#days")
    public List<SubscriptionResponseDTO> getUpcomingRenewals(int days) {
        int windowDays = (days > 0) ? days : 30;
        LocalDate today = LocalDate.now();
        LocalDate endDate = today.plusDays(windowDays);

        List<Subscription> subscriptions = subscriptionRepository.findUpcomingRenewals(today, endDate, SubscriptionStatus.ACTIVE);
        return subscriptions.stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    /**
     * Maps Subscription entity to SubscriptionResponseDTO and populates runtime calculated fields.
     */
    private SubscriptionResponseDTO mapToDTO(Subscription sub) {
        SubscriptionResponseDTO dto = new SubscriptionResponseDTO();
        dto.setId(sub.getId());
        dto.setName(sub.getName());
        dto.setCategory(sub.getCategory());
        dto.setAmount(sub.getAmount());
        dto.setCurrency(sub.getCurrency());
        dto.setBillingFrequency(sub.getBillingFrequency());
        dto.setStartDate(sub.getStartDate());
        dto.setNextRenewalDate(sub.getNextRenewalDate());
        dto.setStatus(sub.getStatus());
        dto.setCancellationDate(sub.getCancellationDate());
        dto.setNotes(sub.getNotes());
        dto.setCreatedAt(sub.getCreatedAt());
        dto.setUpdatedAt(sub.getUpdatedAt());

        // Normalized monthly cost
        BigDecimal monthlyEquivalent = RenewalCalculator.normalizeToMonthly(sub.getAmount(), sub.getBillingFrequency());
        dto.setMonthlyEquivalentAmount(monthlyEquivalent);

        // Days remaining until renewal
        if (sub.getNextRenewalDate() != null) {
            long days = ChronoUnit.DAYS.between(LocalDate.now(), sub.getNextRenewalDate());
            dto.setDaysUntilRenewal(days);
        }

        return dto;
    }
}
