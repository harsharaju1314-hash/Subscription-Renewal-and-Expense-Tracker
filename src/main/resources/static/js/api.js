/**
 * REST API Client for Subscription Renewal and Expense Tracker.
 * Encapsulates fetch() requests to backend Spring Boot endpoints.
 */
const API = {
    baseUrl: '/api/v1',

    /**
     * Internal request helper handling JSON parsing and unified error propagation.
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);

            // Handle HTTP 204 No Content
            if (response.status === 204) {
                return null;
            }

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                let errorMessage = 'An unexpected server error occurred';
                if (data) {
                    if (data.validationErrors) {
                        const errorList = Object.entries(data.validationErrors)
                            .map(([field, msg]) => `${field}: ${msg}`)
                            .join('; ');
                        errorMessage = `Validation error - ${errorList}`;
                    } else if (data.message) {
                        errorMessage = data.message;
                    }
                }
                const error = new Error(errorMessage);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (err) {
            console.error(`API Error on [${options.method || 'GET'}] ${url}:`, err);
            throw err;
        }
    },

    /**
     * Endpoint 1: Create a subscription
     */
    async createSubscription(subscriptionData) {
        return this.request('/subscriptions', {
            method: 'POST',
            body: JSON.stringify(subscriptionData)
        });
    },

    /**
     * Endpoint 2: Fetch paginated & filtered subscriptions
     */
    async getSubscriptions({ category = '', status = '', page = 0, size = 10, sortBy = 'nextRenewalDate', sortDir = 'asc' } = {}) {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        if (status) params.append('status', status);
        params.append('page', page);
        params.append('size', size);
        params.append('sortBy', sortBy);
        params.append('sortDir', sortDir);

        return this.request(`/subscriptions?${params.toString()}`);
    },

    /**
     * Endpoint 3: Get single subscription by ID
     */
    async getSubscriptionById(id) {
        return this.request(`/subscriptions/${id}`);
    },

    /**
     * Endpoint 4: Update existing subscription
     */
    async updateSubscription(id, subscriptionData) {
        return this.request(`/subscriptions/${id}`, {
            method: 'PUT',
            body: JSON.stringify(subscriptionData)
        });
    },

    /**
     * Endpoint 5: Delete subscription
     */
    async deleteSubscription(id) {
        return this.request(`/subscriptions/${id}`, {
            method: 'DELETE'
        });
    },

    /**
     * Endpoint 6: Get upcoming renewals
     */
    async getUpcomingRenewals(days = 30) {
        return this.request(`/subscriptions/upcoming?days=${days}`);
    },

    /**
     * Endpoint 7: Get overall monthly & annual expense summary
     */
    async getExpenseSummary() {
        return this.request('/expenses/summary');
    },

    /**
     * Endpoint 8: Get expenses by category
     */
    async getExpensesByCategory() {
        return this.request('/expenses/by-category');
    }
};
