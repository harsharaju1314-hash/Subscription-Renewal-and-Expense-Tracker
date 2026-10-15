package com.ibm.tracker.controller;

import com.ibm.tracker.dto.CategoryExpenseDTO;
import com.ibm.tracker.dto.MonthlyExpenseSummaryDTO;
import com.ibm.tracker.service.ExpenseService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * REST Controller exposing financial expense aggregation endpoints (Endpoints 7 and 8).
 */
@RestController
@RequestMapping("/api/v1/expenses")
@CrossOrigin(origins = "*")
public class ExpenseController {

    private final ExpenseService expenseService;

    public ExpenseController(ExpenseService expenseService) {
        this.expenseService = expenseService;
    }

    /**
     * Endpoint 7: Retrieve portfolio-wide monthly and annual spending summary.
     * HTTP 200 OK. Cached in Redis.
     */
    @GetMapping("/summary")
    public ResponseEntity<MonthlyExpenseSummaryDTO> getExpenseSummary() {
        MonthlyExpenseSummaryDTO summary = expenseService.getExpenseSummary();
        return ResponseEntity.ok(summary);
    }

    /**
     * Endpoint 8: Retrieve normalized monthly expenses broken down by category with percentage shares.
     * HTTP 200 OK. Cached in Redis.
     */
    @GetMapping("/by-category")
    public ResponseEntity<List<CategoryExpenseDTO>> getExpensesByCategory() {
        List<CategoryExpenseDTO> categories = expenseService.getExpensesByCategory();
        return ResponseEntity.ok(categories);
    }
}
