package com.ibm.tracker.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.tracker.dto.PagedResponseDTO;
import com.ibm.tracker.dto.SubscriptionRequestDTO;
import com.ibm.tracker.dto.SubscriptionResponseDTO;
import com.ibm.tracker.entity.BillingFrequency;
import com.ibm.tracker.entity.SubscriptionStatus;
import com.ibm.tracker.exception.GlobalExceptionHandler;
import com.ibm.tracker.exception.ResourceNotFoundException;
import com.ibm.tracker.service.SubscriptionService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Collections;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(SubscriptionController.class)
@Import(GlobalExceptionHandler.class)
@DisplayName("SubscriptionController Integration Tests - REST Endpoints 1 to 6")
class SubscriptionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private SubscriptionService subscriptionService;

    @Test
    @DisplayName("POST /api/v1/subscriptions: Should return 201 Created on valid input")
    void testCreateSubscription_Success() throws Exception {
        SubscriptionRequestDTO request = new SubscriptionRequestDTO(
                "Netflix", "STREAMING", BigDecimal.valueOf(15.99), "USD",
                BillingFrequency.MONTHLY, LocalDate.of(2026, 1, 1), SubscriptionStatus.ACTIVE, "Family plan"
        );

        SubscriptionResponseDTO response = new SubscriptionResponseDTO();
        response.setId(1L);
        response.setName("Netflix");
        response.setCategory("STREAMING");
        response.setAmount(BigDecimal.valueOf(15.99));
        response.setBillingFrequency(BillingFrequency.MONTHLY);
        response.setNextRenewalDate(LocalDate.of(2026, 2, 1));
        response.setStatus(SubscriptionStatus.ACTIVE);

        when(subscriptionService.createSubscription(any(SubscriptionRequestDTO.class))).thenReturn(response);

        mockMvc.perform(post("/api/v1/subscriptions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.name").value("Netflix"))
                .andExpect(jsonPath("$.amount").value(15.99));
    }

    @Test
    @DisplayName("POST /api/v1/subscriptions: Should return 400 Bad Request when validation fails")
    void testCreateSubscription_ValidationFailure() throws Exception {
        // Missing name, negative amount, null start date
        SubscriptionRequestDTO invalidRequest = new SubscriptionRequestDTO(
                "", "STREAMING", BigDecimal.valueOf(-5.00), "USD",
                BillingFrequency.MONTHLY, null, SubscriptionStatus.ACTIVE, null
        );

        mockMvc.perform(post("/api/v1/subscriptions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.validationErrors.name").exists())
                .andExpect(jsonPath("$.validationErrors.amount").exists())
                .andExpect(jsonPath("$.validationErrors.startDate").exists());
    }

    @Test
    @DisplayName("GET /api/v1/subscriptions/{id}: Should return 200 OK when record exists")
    void testGetSubscriptionById_Success() throws Exception {
        SubscriptionResponseDTO response = new SubscriptionResponseDTO();
        response.setId(1L);
        response.setName("Spotify");
        response.setAmount(BigDecimal.valueOf(9.99));

        when(subscriptionService.getSubscriptionById(1L)).thenReturn(response);

        mockMvc.perform(get("/api/v1/subscriptions/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.name").value("Spotify"));
    }

    @Test
    @DisplayName("GET /api/v1/subscriptions/{id}: Should return 404 Not Found when ID does not exist")
    void testGetSubscriptionById_NotFound() throws Exception {
        when(subscriptionService.getSubscriptionById(999L))
                .thenThrow(new ResourceNotFoundException("Subscription", "id", 999L));

        mockMvc.perform(get("/api/v1/subscriptions/999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("Not Found"));
    }

    @Test
    @DisplayName("DELETE /api/v1/subscriptions/{id}: Should return 204 No Content on successful deletion")
    void testDeleteSubscription_Success() throws Exception {
        doNothing().when(subscriptionService).deleteSubscription(1L);

        mockMvc.perform(delete("/api/v1/subscriptions/1"))
                .andExpect(status().isNoContent());

        verify(subscriptionService, times(1)).deleteSubscription(1L);
    }

    @Test
    @DisplayName("GET /api/v1/subscriptions/upcoming: Should return 200 OK with upcoming list")
    void testGetUpcomingRenewals() throws Exception {
        SubscriptionResponseDTO response = new SubscriptionResponseDTO();
        response.setId(1L);
        response.setName("AWS");
        response.setDaysUntilRenewal(5);

        when(subscriptionService.getUpcomingRenewals(30)).thenReturn(Collections.singletonList(response));

        mockMvc.perform(get("/api/v1/subscriptions/upcoming?days=30"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(1))
                .andExpect(jsonPath("$[0].name").value("AWS"));
    }
}
