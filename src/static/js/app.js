// Kondate - 献立管理システム JavaScript

console.log('Kondate system loaded');

// グローバルエラーハンドリング
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// API通信ユーティリティ
const api = {
    baseURL: '',  // FastAPIのベースURL（相対パスでOK）

    async request(url, options = {}) {
        try {
            const response = await fetch(this.baseURL + url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('API Response:', data);  // デバッグ用
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    async getDishes(params = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `/api/dishes?${query}` : '/api/dishes';
        return this.request(url);
    },

    async getDish(id) {
        return this.request(`/api/dishes/${id}`);
    },

    async createDish(data) {
        return this.request('/api/dishes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },

    async updateDish(id, data) {
        return this.request(`/api/dishes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },

    async deleteDish(id) {
        return this.request(`/api/dishes/${id}`, {
            method: 'DELETE'
        });
    },

    async searchByIngredients(query, n = 5) {
        return this.request(`/api/search/ingredients?q=${encodeURIComponent(query)}&n=${n}`);
    },

    async suggest(prefer = null) {
        const params = prefer ? `?prefer=${prefer}` : '';
        return this.request(`/api/suggest${params}`);
    }
};

// ユーティリティ関数
const utils = {
    formatNutrition(value, unit) {
        if (value === null || value === undefined) return '-';
        return `${value}${unit}`;
    },

    showNotification(message, type = 'info') {
        // TODO: 通知UIを実装
        console.log(`[${type}] ${message}`);
    }
};

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    // ページ固有の初期化処理は各テンプレート内で実行
});
