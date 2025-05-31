/**
 * Forms Module
 * Contains functions for form handling
 */

import { showNotification } from './notifications.js';
import { reloadUpcomingWorkouts } from './upcoming-workouts.js';

/**
 * Bind add schedule form
 */
export function bindAddScheduleForm() {
    const form = document.getElementById('add-schedule-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
            if (response.redirected || response.ok) {
                await reloadUpcomingWorkouts();
                showNotification('Тренировка добавлена!', 'success');
                form.reset();
            } else {
                showNotification('Ошибка при добавлении тренировки', 'error');
            }
        });
    }
}

/**
 * Валидация формы
 * @param {HTMLFormElement} form - Форма для валидации
 * @returns {boolean} - Результат валидации
 */
export function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            markInvalid(input, 'Это поле обязательно для заполнения');
            isValid = false;
        } else if (input.type === 'email' && input.value.trim() && !validateEmail(input.value)) {
            markInvalid(input, 'Введите корректный email');
            isValid = false;
        } else if (input.type === 'password' && input.dataset.minLength && input.value.length < parseInt(input.dataset.minLength)) {
            markInvalid(input, `Пароль должен содержать не менее ${input.dataset.minLength} символов`);
            isValid = false;
        } else {
            clearInvalid(input);
        }
    });
    
    return isValid;
}

/**
 * Валидация email
 * @param {string} email - Email для валидации
 * @returns {boolean} - Результат валидации
 */
export function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Отметка поля как невалидного
 * @param {HTMLElement} input - Поле ввода
 * @param {string} message - Сообщение об ошибке
 */
function markInvalid(input, message) {
    input.classList.add('is-invalid');
    
    let errorElement = input.nextElementSibling;
    if (!errorElement || !errorElement.classList.contains('error-message')) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        input.parentNode.insertBefore(errorElement, input.nextSibling);
    }
    
    errorElement.textContent = message;
}

/**
 * Очистка отметки о невалидности поля
 * @param {HTMLElement} input - Поле ввода
 */
function clearInvalid(input) {
    input.classList.remove('is-invalid');
    
    const errorElement = input.nextElementSibling;
    if (errorElement && errorElement.classList.contains('error-message')) {
        errorElement.parentNode.removeChild(errorElement);
    }
}
