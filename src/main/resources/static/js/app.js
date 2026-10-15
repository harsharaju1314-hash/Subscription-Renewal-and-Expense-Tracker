/**
 * Dashboard UI Controller for Subscription Renewal and Expense Tracker.
 * Manages frontend state, table rendering, filtering, pagination, and modal interactions.
 */

// Application State
const state = {
    page: 0,
    size: 10,
    totalPages: 1,
    totalElements: 0,
    category: '',
    status: 'ACTIVE',
    sortBy: 'nextRenewalDate',
    sortDir: 'asc',
    editingId: null
};

// DOM Element References
const elements = {
    // KPI Cards
    kpiMonthlySpend: document.getElementById('kpiMonthlySpend'),
    kpiMonthlyCount: document.getElementById('kpiMonthlyCount'),
    kpiAnnualSpend: document.getElementById('kpiAnnualSpend'),
    kpiActiveCount: document.getElementById('kpiActiveCount'),
    kpiUpcomingCount: document.getElementById('kpiUpcomingCount'),

    // Table & Filters
    subscriptionTable: document.getElementById('subscriptionTable'),
    subscriptionTableBody: document.getElementById('subscriptionTableBody'),
    tableLoading: document.getElementById('tableLoading'),
    emptyState: document.getElementById('emptyState'),
    recordCountBadge: document.getElementById('recordCountBadge'),
    filterCategory: document.getElementById('filterCategory'),
    filterStatus: document.getElementById('filterStatus'),
    sortField: document.getElementById('sortField'),
    sortDirection: document.getElementById('sortDirection'),
    btnRefreshData: document.getElementById('btnRefreshData'),

    // Pagination
    currentPageNum: document.getElementById('currentPageNum'),
    totalPagesNum: document.getElementById('totalPagesNum'),
    btnPrevPage: document.getElementById('btnPrevPage'),
    btnNextPage: document.getElementById('btnNextPage'),

    // Sidebar
    upcomingFeedList: document.getElementById('upcomingFeedList'),
    upcomingFeedCount: document.getElementById('upcomingFeedCount'),
    categoryBreakdownList: document.getElementById('categoryBreakdownList'),

    // Modal & Form
    subscriptionModal: document.getElementById('subscriptionModal'),
    subscriptionForm: document.getElementById('subscriptionForm'),
    modalTitle: document.getElementById('modalTitle'),
    formSubscriptionId: document.getElementById('formSubscriptionId'),
    formName: document.getElementById('formName'),
    formCategory: document.getElementById('formCategory'),
    formBillingFrequency: document.getElementById('formBillingFrequency'),
    formAmount: document.getElementById('formAmount'),
    formCurrency: document.getElementById('formCurrency'),
    formStartDate: document.getElementById('formStartDate'),
    formStatus: document.getElementById('formStatus'),
    formNotes: document.getElementById('formNotes'),
    formErrorBanner: document.getElementById('formErrorBanner'),
    btnOpenAddModal: document.getElementById('btnOpenAddModal'),
    btnModalClose: document.getElementById('btnModalClose'),
    btnModalCancel: document.getElementById('btnModalCancel'),
    toastContainer: document.getElementById('toastContainer')
};

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadDashboard();
});

/**
 * Attaches event listeners to interactive DOM elements.
 */
function initEventListeners() {
    // Refresh button
    elements.btnRefreshData.addEventListener('click', () => {
        loadDashboard();
        showToast('Dashboard refreshed from REST APIs', 'info');
    });

    // Filtering & Sorting
    elements.filterCategory.addEventListener('change', (e) => {
        state.category = e.target.value;
        state.page = 0;
        loadSubscriptions();
    });

    elements.filterStatus.addEventListener('change', (e) => {
        state.status = e.target.value;
        state.page = 0;
        loadSubscriptions();
    });

    elements.sortField.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        loadSubscriptions();
    });

    elements.sortDirection.addEventListener('change', (e) => {
        state.sortDir = e.target.value;
        loadSubscriptions();
    });

    // Pagination buttons
    elements.btnPrevPage.addEventListener('click', () => {
        if (state.page > 0) {
            state.page--;
            loadSubscriptions();
        }
    });

    elements.btnNextPage.addEventListener('click', () => {
        if (state.page < state.totalPages - 1) {
            state.page++;
            loadSubscriptions();
        }
    });

    // Modal controls
    elements.btnOpenAddModal.addEventListener('click', openCreateModal);
    elements.btnModalClose.addEventListener('click', closeModal);
    elements.btnModalCancel.addEventListener('click', closeModal);

    // Form submission
    elements.subscriptionForm.addEventListener('submit', handleFormSubmit);

    // Close modal on backdrop click
    elements.subscriptionModal.addEventListener('click', (e) => {
        if (e.target === elements.subscriptionModal) {
            closeModal();
        }
    });
}

/**
 * Orchestrates full dashboard reload across all API endpoints in parallel.
 */
async function loadDashboard() {
    await Promise.all([
        loadSummaryKPIs(),
        loadSubscriptions(),
        loadUpcomingRenewals(),
        loadCategoryBreakdown()
    ]);
}

/**
 * Fetches and displays portfolio KPI metrics (Endpoint 7).
 */
async function loadSummaryKPIs() {
    try {
        const summary = await API.getExpenseSummary();
        if (summary) {
            elements.kpiMonthlySpend.textContent = `$${Number(summary.totalMonthlyExpense).toFixed(2)}`;
            elements.kpiAnnualSpend.textContent = `$${Number(summary.totalAnnualExpense).toFixed(2)}`;
            elements.kpiActiveCount.textContent = summary.totalActiveSubscriptions;
            elements.kpiMonthlyCount.textContent = `Across ${summary.totalActiveSubscriptions} active service${summary.totalActiveSubscriptions === 1 ? '' : 's'}`;
        }
    } catch (err) {
        showToast('Failed to load spending summary', 'error');
    }
}

/**
 * Fetches paginated subscription records (Endpoint 2).
 */
async function loadSubscriptions() {
    elements.tableLoading.classList.remove('hidden');
    elements.emptyState.classList.add('hidden');
    elements.subscriptionTableBody.innerHTML = '';

    try {
        const response = await API.getSubscriptions({
            category: state.category,
            status: state.status,
            page: state.page,
            size: state.size,
            sortBy: state.sortBy,
            sortDir: state.sortDir
        });

        elements.tableLoading.classList.add('hidden');

        if (!response || !response.content || response.content.length === 0) {
            elements.emptyState.classList.remove('hidden');
            elements.recordCountBadge.textContent = '0 total';
            updatePaginationControls(0, 0, 0);
            return;
        }

        state.totalPages = response.totalPages;
        state.totalElements = response.totalElements;
        elements.recordCountBadge.textContent = `${response.totalElements} total`;

        renderTable(response.content);
        updatePaginationControls(response.pageNumber, response.totalPages, response.totalElements);
    } catch (err) {
        elements.tableLoading.classList.add('hidden');
        elements.emptyState.classList.remove('hidden');
        showToast('Failed to load subscriptions', 'error');
    }
}

/**
 * Renders subscription records into table rows.
 */
function renderTable(subscriptions) {
    elements.subscriptionTableBody.innerHTML = '';

    subscriptions.forEach(sub => {
        const tr = document.createElement('tr');

        // Status badge class
        let statusBadgeClass = 'badge-active';
        if (sub.status === 'PAUSED') statusBadgeClass = 'badge-paused';
        if (sub.status === 'CANCELLED') statusBadgeClass = 'badge-cancelled';

        // Urgency badge if renewal is due within 7 days
        const daysLeft = sub.daysUntilRenewal;
        let renewalBadge = '';
        if (daysLeft >= 0 && daysLeft <= 7 && sub.status === 'ACTIVE') {
            renewalBadge = `<span class="badge badge-urgent" style="margin-left: 6px;">Due in ${daysLeft}d</span>`;
        } else if (daysLeft < 0 && sub.status === 'ACTIVE') {
            renewalBadge = `<span class="badge badge-cancelled" style="margin-left: 6px;">Overdue</span>`;
        }

        tr.innerHTML = `
            <td>
                <div class="sub-name-cell">${escapeHtml(sub.name)}</div>
                ${sub.notes ? `<div class="sub-notes">${escapeHtml(sub.notes)}</div>` : ''}
            </td>
            <td><span class="badge badge-category">${escapeHtml(sub.category)}</span></td>
            <td>${formatFrequency(sub.billingFrequency)}</td>
            <td class="sub-cost">$${Number(sub.amount).toFixed(2)} <span style="font-size: 0.7rem; color: #94a3b8;">${escapeHtml(sub.currency)}</span></td>
            <td class="sub-cost" style="color: #2563eb;">$${Number(sub.monthlyEquivalentAmount).toFixed(2)}/mo</td>
            <td>
                <span>${sub.nextRenewalDate || 'N/A'}</span>
                ${renewalBadge}
            </td>
            <td><span class="badge ${statusBadgeClass}">${sub.status}</span></td>
            <td class="text-right">
                <button class="btn btn-sm btn-edit-outline" onclick="openEditModal(${sub.id})" title="Edit Subscription">Edit</button>
                <button class="btn btn-sm btn-danger-outline" onclick="deleteSubscription(${sub.id}, '${escapeHtml(sub.name)}')" title="Delete Subscription">Delete</button>
            </td>
        `;
        elements.subscriptionTableBody.appendChild(tr);
    });
}

/**
 * Updates pagination state and button states.
 */
function updatePaginationControls(currentPage, totalPages, totalElements) {
    elements.currentPageNum.textContent = totalPages === 0 ? 0 : currentPage + 1;
    elements.totalPagesNum.textContent = totalPages;

    elements.btnPrevPage.disabled = currentPage <= 0;
    elements.btnNextPage.disabled = currentPage >= totalPages - 1;
}

/**
 * Fetches upcoming renewals within 30 days (Endpoint 6).
 */
async function loadUpcomingRenewals() {
    try {
        const renewals = await API.getUpcomingRenewals(30);
        elements.upcomingFeedList.innerHTML = '';
        elements.kpiUpcomingCount.textContent = renewals.length;
        elements.upcomingFeedCount.textContent = `${renewals.length} due`;

        if (!renewals || renewals.length === 0) {
            elements.upcomingFeedList.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: #94a3b8; font-size: 0.82rem;">
                    No upcoming renewals in the next 30 days.
                </div>
            `;
            return;
        }

        renewals.forEach(sub => {
            const item = document.createElement('div');
            item.className = 'feed-item';
            const daysLeft = sub.daysUntilRenewal;
            const badgeClass = daysLeft <= 3 ? 'badge-urgent' : 'badge-info';

            item.innerHTML = `
                <div>
                    <div class="feed-title">${escapeHtml(sub.name)}</div>
                    <div class="feed-meta">${sub.nextRenewalDate} • $${Number(sub.amount).toFixed(2)} (${formatFrequency(sub.billingFrequency)})</div>
                </div>
                <div>
                    <span class="badge ${badgeClass}">${daysLeft === 0 ? 'Today' : `${daysLeft}d left`}</span>
                </div>
            `;
            elements.upcomingFeedList.appendChild(item);
        });
    } catch (err) {
        console.error('Error fetching upcoming renewals:', err);
    }
}

/**
 * Fetches category expense breakdown (Endpoint 8).
 */
async function loadCategoryBreakdown() {
    try {
        const categories = await API.getExpensesByCategory();
        elements.categoryBreakdownList.innerHTML = '';

        if (!categories || categories.length === 0) {
            elements.categoryBreakdownList.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: #94a3b8; font-size: 0.82rem;">
                    No active category expenses recorded.
                </div>
            `;
            return;
        }

        categories.forEach(cat => {
            const row = document.createElement('div');
            row.className = 'breakdown-row';
            const pct = Number(cat.percentageOfTotal).toFixed(1);

            row.innerHTML = `
                <div class="breakdown-label-group">
                    <span class="breakdown-cat">${escapeHtml(cat.category)} (${cat.subscriptionCount})</span>
                    <span class="breakdown-amount">$${Number(cat.totalMonthlyExpense).toFixed(2)}/mo (${pct}%)</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: ${pct}%;"></div>
                </div>
            `;
            elements.categoryBreakdownList.appendChild(row);
        });
    } catch (err) {
        console.error('Error fetching category breakdown:', err);
    }
}

/**
 * Opens Create Subscription Modal.
 */
function openCreateModal() {
    state.editingId = null;
    elements.subscriptionForm.reset();
    elements.modalTitle.textContent = 'Add Subscription';
    elements.formSubscriptionId.value = '';
    elements.formStatus.value = 'ACTIVE';
    elements.formCurrency.value = 'USD';
    elements.formBillingFrequency.value = 'MONTHLY';
    elements.formStartDate.value = new Date().toISOString().split('T')[0];
    elements.formErrorBanner.classList.add('hidden');
    elements.subscriptionModal.classList.remove('hidden');
}

/**
 * Opens Edit Subscription Modal and populates data (Endpoint 3).
 */
async function openEditModal(id) {
    try {
        const sub = await API.getSubscriptionById(id);
        state.editingId = id;
        elements.modalTitle.textContent = 'Edit Subscription';
        elements.formSubscriptionId.value = sub.id;
        elements.formName.value = sub.name;
        elements.formCategory.value = sub.category;
        elements.formBillingFrequency.value = sub.billingFrequency;
        elements.formAmount.value = sub.amount;
        elements.formCurrency.value = sub.currency;
        elements.formStartDate.value = sub.startDate;
        elements.formStatus.value = sub.status;
        elements.formNotes.value = sub.notes || '';
        elements.formErrorBanner.classList.add('hidden');
        elements.subscriptionModal.classList.remove('hidden');
    } catch (err) {
        showToast('Failed to load subscription details', 'error');
    }
}

/**
 * Closes the modal.
 */
function closeModal() {
    elements.subscriptionModal.classList.add('hidden');
    elements.subscriptionForm.reset();
    state.editingId = null;
}

/**
 * Handles Create / Update Form Submission (Endpoint 1 & 4).
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    elements.formErrorBanner.classList.add('hidden');

    const payload = {
        name: elements.formName.value.trim(),
        category: elements.formCategory.value.trim().toUpperCase(),
        billingFrequency: elements.formBillingFrequency.value,
        amount: parseFloat(elements.formAmount.value),
        currency: elements.formCurrency.value.trim().toUpperCase() || 'USD',
        startDate: elements.formStartDate.value,
        status: elements.formStatus.value,
        notes: elements.formNotes.value.trim() || null
    };

    // Client-side quick check
    if (!payload.name || !payload.category || isNaN(payload.amount) || payload.amount <= 0 || !payload.startDate) {
        showFormError('Please fill in all required fields with valid values (Amount must be > 0).');
        return;
    }

    try {
        if (state.editingId) {
            await API.updateSubscription(state.editingId, payload);
            showToast('Subscription updated successfully (Redis cache evicted)', 'success');
        } else {
            await API.createSubscription(payload);
            showToast('Subscription created successfully (Redis cache evicted)', 'success');
        }

        closeModal();
        await loadDashboard();
    } catch (err) {
        showFormError(err.message || 'Failed to save subscription.');
    }
}

/**
 * Handles Subscription Deletion with confirmation (Endpoint 5).
 */
async function deleteSubscription(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
        return;
    }

    try {
        await API.deleteSubscription(id);
        showToast(`Subscription "${name}" deleted (Redis cache evicted)`, 'success');
        await loadDashboard();
    } catch (err) {
        showToast(err.message || 'Failed to delete subscription', 'error');
    }
}

/**
 * Displays an error inside the modal form.
 */
function showFormError(message) {
    elements.formErrorBanner.textContent = message;
    elements.formErrorBanner.classList.remove('hidden');
}

/**
 * Displays floating toast notifications.
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s ease';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

/**
 * Formats enum frequency into readable label.
 */
function formatFrequency(frequency) {
    const labels = {
        'WEEKLY': 'Weekly',
        'BI_WEEKLY': 'Bi-Weekly',
        'MONTHLY': 'Monthly',
        'QUARTERLY': 'Quarterly',
        'SEMI_ANNUALLY': 'Semi-Annually',
        'ANNUALLY': 'Annually'
    };
    return labels[frequency] || frequency;
}

/**
 * Escapes HTML strings to prevent XSS injection.
 */
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Global modal triggers for HTML onclick bindings
window.openCreateModal = openCreateModal;
window.openEditModal = openEditModal;
window.deleteSubscription = deleteSubscription;
