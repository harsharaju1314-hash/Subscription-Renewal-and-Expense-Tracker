package com.tracker.controller;

import com.tracker.dto.CategoryExpenseDTO;
import com.tracker.dto.MonthlyExpenseSummaryDTO;
import com.tracker.exception.GlobalExceptionHandler;
import com.tracker.service.ExpenseService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Collections;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(ExpenseController.class)
@Import(GlobalExceptionHandler.class)
@DisplayName("ExpenseController Integration Tests - Endpoints 7 & 8")
class ExpenseControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ExpenseService expenseService;

    @Test
    @DisplayName("GET /api/v1/expenses/summary: Should return 200 OK with summary metrics")
    void testGetExpenseSummary() throws Exception {
        MonthlyExpenseSummaryDTO summary = new MonthlyExpenseSummaryDTO(
                5, BigDecimal.valueOf(120.50), BigDecimal.valueOf(1446.00), "USD", LocalDateTime.now()
        );

        when(expenseService.getExpenseSummary()).thenReturn(summary);

        mockMvc.perform(get("/api/v1/expenses/summary"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalActiveSubscriptions").value(5))
                .andExpect(jsonPath("$.totalMonthlyExpense").value(120.50))
                .andExpect(jsonPath("$.totalAnnualExpense").value(1446.00));
    }

    @Test
    @DisplayName("GET /api/v1/expenses/by-category: Should return 200 OK with category breakdowns")
    void testGetExpensesByCategory() throws Exception {
        CategoryExpenseDTO dto = new CategoryExpenseDTO(
                "SOFTWARE", 2, BigDecimal.valueOf(45.00), BigDecimal.valueOf(37.34)
        );

        when(expenseService.getExpensesByCategory()).thenReturn(Collections.singletonList(dto));

        mockMvc.perform(get("/api/v1/expenses/by-category"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].category").value("SOFTWARE"))
                .andExpect(jsonPath("$[0].subscriptionCount").value(2))
                .andExpect(jsonPath("$[0].totalMonthlyExpense").value(45.00))
                .andExpect(jsonPath("$[0].percentageOfTotal").value(37.34));
    }
}
