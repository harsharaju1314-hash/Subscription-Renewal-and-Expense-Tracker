package com.ibm.tracker.service;

import com.ibm.tracker.dto.PagedResponseDTO;
import com.ibm.tracker.dto.SubscriptionRequestDTO;
import com.ibm.tracker.dto.SubscriptionResponseDTO;
import com.ibm.tracker.entity.BillingFrequency;
import com.ibm.tracker.entity.Subscription;
import com.ibm.tracker.entity.SubscriptionStatus;
import com.ibm.tracker.exception.ResourceNotFoundException;
import com.ibm.tracker.repository.SubscriptionRepository;
import com.ibm.tracker.service.impl.SubscriptionServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("SubscriptionService Unit Tests - CRUD & Business Logic")
class SubscriptionServiceTest {

    @Mock
    private SubscriptionRepository subscriptionRepository;

    @InjectMocks
    private SubscriptionServiceImpl subscriptionService;

    private Subscription testSubscription;
    private SubscriptionRequestDTO testRequest;

    @BeforeEach
    void setUp() {
        testSubscription = new Subscription(
                1L,
                "GitHub Copilot",
                "SOFTWARE",
                BigDecimal.valueOf(10.00),
                "USD",
                BillingFrequency.MONTHLY,
                LocalDate.now().minusMonths(2),
                LocalDate.now().plusDays(10),
                SubscriptionStatus.ACTIVE,
                null,
                "Dev license"
        );
        testSubscription.setCreatedAt(LocalDateTime.now().minusDays(30));
        testSubscription.setUpdatedAt(LocalDateTime.now());

        testRequest = new SubscriptionRequestDTO(
                "GitHub Copilot",
                "SOFTWARE",
                new BigDecimal("10.00"),
                "USD",
                BillingFrequency.MONTHLY,
                LocalDate.now().plusDays(1),
                SubscriptionStatus.ACTIVE,
                "Dev license"
        );
    }

    @Test
    @DisplayName("createSubscription: Should save entity and calculate initial renewal date")
    void testCreateSubscription() {
        when(subscriptionRepository.save(any(Subscription.class))).thenAnswer(invocation -> {
            Subscription sub = invocation.getArgument(0);
            sub.setId(100L);
            sub.setCreatedAt(LocalDateTime.now());
            sub.setUpdatedAt(LocalDateTime.now());
            return sub;
        });

        SubscriptionResponseDTO response = subscriptionService.createSubscription(testRequest);

        assertNotNull(response);
        assertEquals(100L, response.getId());
        assertEquals("GitHub Copilot", response.getName());
        assertEquals("SOFTWARE", response.getCategory());
        assertEquals(new BigDecimal("10.00"), response.getAmount());
        assertNotNull(response.getNextRenewalDate());
        verify(subscriptionRepository, times(1)).save(any(Subscription.class));
    }

    @Test
    @DisplayName("getSubscriptionById: Should return DTO when found")
    void testGetSubscriptionById_Success() {
        when(subscriptionRepository.findById(1L)).thenReturn(Optional.of(testSubscription));

        SubscriptionResponseDTO response = subscriptionService.getSubscriptionById(1L);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals("GitHub Copilot", response.getName());
        assertEquals(new BigDecimal("10.00"), response.getMonthlyEquivalentAmount());
    }

    @Test
    @DisplayName("getSubscriptionById: Should throw ResourceNotFoundException when ID does not exist")
    void testGetSubscriptionById_NotFound() {
        when(subscriptionRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> subscriptionService.getSubscriptionById(999L));
    }

    @Test
    @DisplayName("updateSubscription: Should update fields and recalculate renewal on frequency change")
    void testUpdateSubscription_Success() {
        when(subscriptionRepository.findById(1L)).thenReturn(Optional.of(testSubscription));
        when(subscriptionRepository.save(any(Subscription.class))).thenAnswer(invocation -> invocation.getArgument(0));

        testRequest.setBillingFrequency(BillingFrequency.ANNUALLY);
        testRequest.setName("GitHub Copilot Enterprise");

        SubscriptionResponseDTO updated = subscriptionService.updateSubscription(1L, testRequest);

        assertNotNull(updated);
        assertEquals("GitHub Copilot Enterprise", updated.getName());
        assertEquals(BillingFrequency.ANNUALLY, updated.getBillingFrequency());
        verify(subscriptionRepository, times(1)).save(any(Subscription.class));
    }

    @Test
    @DisplayName("deleteSubscription: Should delete entity from repository")
    void testDeleteSubscription_Success() {
        when(subscriptionRepository.findById(1L)).thenReturn(Optional.of(testSubscription));
        doNothing().when(subscriptionRepository).delete(testSubscription);

        assertDoesNotThrow(() -> subscriptionService.deleteSubscription(1L));
        verify(subscriptionRepository, times(1)).delete(testSubscription);
    }

    @Test
    @DisplayName("getAllSubscriptions: Should return paginated DTO list")
    void testGetAllSubscriptions() {
        Page<Subscription> page = new PageImpl<>(Collections.singletonList(testSubscription));
        when(subscriptionRepository.findAll(any(Pageable.class))).thenReturn(page);

        PagedResponseDTO<SubscriptionResponseDTO> response = subscriptionService.getAllSubscriptions(
                null, null, 0, 10, "nextRenewalDate", "asc"
        );

        assertNotNull(response);
        assertEquals(1, response.getContent().size());
        assertEquals(1, response.getTotalElements());
        assertEquals(0, response.getPageNumber());
    }

    @Test
    @DisplayName("getUpcomingRenewals: Should query renewals within date window")
    void testGetUpcomingRenewals() {
        when(subscriptionRepository.findUpcomingRenewals(any(LocalDate.class), any(LocalDate.class), eq(SubscriptionStatus.ACTIVE)))
                .thenReturn(Collections.singletonList(testSubscription));

        List<SubscriptionResponseDTO> renewals = subscriptionService.getUpcomingRenewals(30);

        assertNotNull(renewals);
        assertEquals(1, renewals.size());
        assertEquals("GitHub Copilot", renewals.get(0).getName());
    }
}
