/**
 * AJAX Module
 * Contains functions for AJAX requests and data fetching
 */

/**
 * Send AJAX request
 * @param {string} url - URL for request
 * @param {string} method - Request method (GET, POST, PUT, DELETE)
 * @param {Object} data - Data to send
 * @param {Function} callback - Callback function on success
 * @param {Function} errorCallback - Callback function on error
 */
export function sendAjaxRequest(url, method, data, callback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            try {
                const response = JSON.parse(xhr.responseText);
                callback(response);
            } catch (e) {
                callback(xhr.responseText);
            }
        } else {
            if (errorCallback) {
                errorCallback(xhr.status, xhr.responseText);
            } else {
                // showNotification will be imported in main.js
                console.error('Произошла ошибка при выполнении запроса');
            }
        }
    };
    
    xhr.onerror = function() {
        if (errorCallback) {
            errorCallback(0, 'Сетевая ошибка');
        } else {
            // showNotification will be imported in main.js
            console.error('Сетевая ошибка');
        }
    };
    
    xhr.send(JSON.stringify(data));
}

/**
 * Fetch HTML content
 * @param {string} url - URL to fetch
 * @returns {Promise<string>} - HTML content
 */
export async function fetchHtml(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.text();
    throw new Error('Ошибка загрузки');
}

/**
 * Fetch JSON data
 * @param {string} url - URL to fetch
 * @returns {Promise<Object>} - JSON data
 */
export async function fetchJson(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.json();
    throw new Error('Ошибка загрузки');
}

/**
 * Update dashboard statistics
 */
export async function updateDashboardStats() {
    const resp = await fetch('/dashboard/stats-json');
    if (resp.ok) {
        const stats = await resp.json();
        document.getElementById('total-workouts').textContent = stats.total_workouts;
        document.getElementById('total-minutes').textContent = stats.total_minutes;
        document.getElementById('total-calories').textContent = stats.total_calories;
        document.getElementById('achievements-count').textContent = stats.achievements_count;
    }
}
