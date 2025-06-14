/**
 * Модуль для работы с уведомлениями
 */
import { showNotification } from './modules/utils.js';

// Реэкспортируем функцию showNotification
export { showNotification };

// Дополнительные функции для работы с уведомлениями
export function showSuccessNotification(message) {
    showNotification(message, 'success');
}

export function showErrorNotification(message) {
    showNotification(message, 'error');
}

export function showInfoNotification(message) {
    showNotification(message, 'info');
} 