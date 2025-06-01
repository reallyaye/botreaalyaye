/**
 * Главный файл инициализации приложения
 * Импортирует модули и инициализирует их
 */

// Импорты из модулей
import { initUI } from './ui-init.js';
import { bindProfileTabs } from './profile.js';
import { bindWorkoutCardHandlers, updateWorkoutsList } from './workouts.js';
import { bindUpcomingWorkoutHandlers, reloadUpcomingWorkouts } from './upcoming-workouts.js';
import { bindAddScheduleForm } from './forms.js';
import { updateGoalsProgress } from './goals.js';
import { showNotification } from './notifications.js';

// Глобальные переменные для таймера тренировок
let timerInterval = null;
let timerStart = null;
let timerActivity = '';
let timerScheduleId = null;

/**
 * Инициализация стилей уведомлений
 * Проверяет, не добавлены ли стили ранее
 */
function initNotificationStyles() {
    if (!document.getElementById('custom-toast-style')) {
        const style = document.createElement('style');
        style.id = 'custom-toast-style';
        style.innerHTML = `
            .custom-toast {
                position: fixed;
                top: 30px;
                right: 30px;
                z-index: 9999;
                padding: 16px 28px;
                border-radius: 8px;
                font-size: 1.1em;
                box-shadow: 0 2px 12px rgba(0,0,0,0.12);
                opacity: 0;
                pointer-events: none;
                transition: opacity .3s, transform .3s;
                transform: translateY(-20px);
            }
            .custom-toast.show {
                opacity: 1;
                pointer-events: auto;
                transform: translateY(0);
            }
            .toast-success {
                background: #4caf50;
                color: #fff;
            }
            .toast-error {
                background: #e53935;
                color: #fff;
            }
            .toast-info {
                background: #2196f3;
                color: #fff;
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Отображение уведомления
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип уведомления (success, error, info)
 * @param {number} duration - Длительность отображения в миллисекундах
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `custom-toast toast-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Обновление статистики на дашборде
 */
async function updateDashboardStats() {
    try {
        const resp = await fetch('/dashboard/stats-json', { signal: AbortSignal.timeout(10000) });
        if (!resp.ok) throw new Error('Ошибка загрузки статистики');
        const stats = await resp.json();
        document.getElementById('total-workouts').textContent = stats.total_workouts;
        document.getElementById('total-minutes').textContent = stats.total_minutes;
        document.getElementById('total-calories').textContent = stats.total_calories;
        document.getElementById('achievements-count').textContent = stats.achievements_count;
    } catch (err) {
        console.error('Ошибка при обновлении статистики:', err);
        showNotification('Ошибка загрузки статистики', 'error');
    }
}

/**
 * Привязка обработчиков для таймера
 */
function bindTimerHandlers() {
    document.body.addEventListener('click', async function (e) {
        // Начать тренировку с таймером
        if (e.target.classList.contains('start-schedule-btn')) {
            const id = e.target.dataset.id;
            try {
                const resp = await fetch(`/dashboard/schedule-data/${id}`, { signal: AbortSignal.timeout(10000) });
                if (!resp.ok) throw new Error('Ошибка загрузки данных');
                const data = await resp.json();
                timerActivity = data.activity;
                timerScheduleId = data.id;
                document.getElementById('timer-activity-title').textContent = data.activity;
                document.getElementById('timer-display').textContent = '00:00:00';
                document.getElementById('start-timer-modal').style.display = 'flex';
                timerStart = Date.now();
                if (timerInterval) clearInterval(timerInterval);
                timerInterval = setInterval(() => {
                    const elapsed = Math.floor((Date.now() - timerStart) / 1000);
                    const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
                    const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
                    const s = String(elapsed % 60).padStart(2, '0');
                    document.getElementById('timer-display').textContent = `${h}:${m}:${s}`;
                }, 1000);
            } catch (err) {
                console.error('Ошибка при запуске таймера:', err);
                showNotification('Ошибка загрузки данных', 'error');
            }
        }

        // Закрыть таймер
        if (e.target.id === 'close-timer-modal') {
            document.getElementById('start-timer-modal').style.display = 'none';
            if (timerInterval) clearInterval(timerInterval);
        }
    });

    // Остановка таймера и сохранение тренировки
    const stopTimerBtn = document.getElementById('stop-timer-btn');
    if (stopTimerBtn) {
        stopTimerBtn.addEventListener('click', async function () {
            if (!timerStart || !timerScheduleId) return;
            const elapsed = Math.floor((Date.now() - timerStart) / 1000);
            try {
                const resp = await fetch(`/dashboard/finish-schedule/${timerScheduleId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration_seconds: elapsed }),
                    signal: AbortSignal.timeout(10000)
                });
                if (!resp.ok) throw new Error('Ошибка сохранения тренировки');
                document.getElementById('start-timer-modal').style.display = 'none';
                if (timerInterval) clearInterval(timerInterval);
                await reloadUpcomingWorkouts();
                await updateDashboardStats();
                showNotification('Тренировка завершена и сохранена!', 'success');
            } catch (err) {
                console.error('Ошибка при сохранении тренировки:', err);
                showNotification('Ошибка при сохранении тренировки', 'error');
            }
        });
    }
}

/**
 * Привязка обработчиков для списка тренировок
 */
function bindWorkoutListHandlers() {
    // Редактирование тренировки
    document.querySelectorAll('.edit-workout-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const id = btn.dataset.id;
            try {
                const resp = await fetch(`/workouts/edit/${id}`, { signal: AbortSignal.timeout(10000) });
                if (!resp.ok) throw new Error('Ошибка загрузки тренировки');
                const w = await resp.json();
                document.getElementById('workout-modal-title').textContent = 'Редактировать тренировку';
                document.getElementById('workout-id').value = w.id;
                document.getElementById('workout-activity').value = w.activity;
                document.getElementById('workout-intensity').value = w.intensity;
                document.getElementById('workout-duration').value = w.duration;
                document.getElementById('workout-comment').value = w.comment || '';
                document.getElementById('workout-modal').style.display = 'flex';
            } catch (err) {
                console.error('Ошибка загрузки тренировки:', err);
                showNotification('Ошибка загрузки тренировки', 'error');
            }
        });
    });

    // Удаление тренировки
    document.querySelectorAll('.delete-workout-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            if (!confirm('Удалить тренировку?')) return;
            const id = btn.dataset.id;
            try {
                const resp = await fetch(`/workouts/delete/${id}`, {
                    method: 'POST',
                    signal: AbortSignal.timeout(10000)
                });
                if (!resp.ok) throw new Error('Ошибка удаления тренировки');
                await updateWorkoutsList();
                showNotification('Тренировка удалена!', 'success');
            } catch (err) {
                console.error('Ошибка при удалении:', err);
                showNotification('Ошибка при удалении', 'error');
            }
        });
    });

    // Открытие модального окна для добавления тренировки
    const addWorkoutBtn = document.getElementById('add-workout-btn');
    if (addWorkoutBtn) {
        addWorkoutBtn.addEventListener('click', function () {
            document.getElementById('workout-modal-title').textContent = 'Добавить тренировку';
            document.getElementById('workout-form').reset();
            document.getElementById('workout-id').value = '';
            document.getElementById('workout-modal').style.display = 'flex';
        });
    }

    // Закрытие модального окна
    const closeWorkoutModal = document.getElementById('close-workout-modal');
    if (closeWorkoutModal) {
        closeWorkoutModal.addEventListener('click', function () {
            document.getElementById('workout-modal').style.display = 'none';
        });
    }

    // Отправка формы добавления/редактирования тренировки
    const workoutForm = document.getElementById('workout-form');
    if (workoutForm) {
        workoutForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const id = document.getElementById('workout-id').value;
            const formData = new FormData(workoutForm);
            const url = id ? `/workouts/edit/${id}` : '/workouts/add';
            try {
                const resp = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    signal: AbortSignal.timeout(10000)
                });
                if (!resp.ok) throw new Error('Ошибка сохранения тренировки');
                document.getElementById('workout-modal').style.display = 'none';
                await updateWorkoutsList();
                showNotification('Тренировка сохранена!', 'success');
            } catch (err) {
                console.error('Ошибка при сохранении:', err);
                showNotification('Ошибка при сохранении', 'error');
            }
        });
    }
}

/**
 * Фильтрация и поиск тренировок
 */
function bindWorkoutFilters() {
    // Фильтрация по типу
    document.querySelectorAll('.chip-filter').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.chip-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const type = btn.dataset.type;
            document.querySelectorAll('.workout-history-card').forEach(card => {
                card.style.display = type === 'all' || card.dataset.type.includes(type) ? '' : 'none';
            });
        });
    });

    // Поиск по названию с дебонсингом
    const workoutSearch = document.getElementById('workout-search');
    if (workoutSearch) {
        const debounce = (fn, delay) => {
            let timeout;
            return (...args) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => fn(...args), delay);
            };
        };
        workoutSearch.addEventListener('input', debounce(function () {
            const val = this.value.toLowerCase();
            document.querySelectorAll('.workout-history-card').forEach(card => {
                const title = card.querySelector('div:nth-child(2) > div').textContent.toLowerCase();
                card.style.display = title.includes(val) ? '' : 'none';
            });
        }, 300));
    }

    // Фильтрация по категориям
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.textContent.trim();
            document.querySelectorAll('.workout-card').forEach(card => {
                card.style.display = filter === 'Все' || card.textContent.includes(filter) ? '' : 'none';
            });
        });
    });
}

/**
 * Обработчики для карточек тренировок
 */
function bindWorkoutCardActions() {
    document.querySelectorAll('.workout-card .workout-actions .btn-primary').forEach(btn => {
        btn.addEventListener('click', function () {
            const card = btn.closest('.workout-card');
            const title = card?.querySelector('.workout-title')?.textContent;
            if (title) {
                window.location.href = `/workouts/start?title=${encodeURIComponent(title)}`;
            } else {
                showNotification('Не удалось определить тренировку', 'error');
            }
        });
    });

    document.querySelectorAll('.workout-card .workout-actions .btn-outline').forEach(btn => {
        btn.addEventListener('click', function () {
            const card = btn.closest('.workout-card');
            const title = card?.querySelector('.workout-title')?.textContent;
            if (title) {
                window.location.href = `/workouts/details?title=${encodeURIComponent(title)}`;
            } else {
                showNotification('Не удалось определить тренировку', 'error');
            }
        });
    });
}

/**
 * Привязка обработчиков для редактирования и удаления предстоящих тренировок
 */
function bindDeleteScheduleForms() {
    document.querySelectorAll('.delete-schedule-form').forEach(form => {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const id = form.dataset.id;
            if (!confirm('Удалить предстоящую тренировку?')) return;
            try {
                const resp = await fetch(`/dashboard/delete-schedule/${id}`, {
                    method: 'POST',
                    signal: AbortSignal.timeout(10000)
                });
                if (!resp.ok) throw new Error('Ошибка удаления тренировки');
                await reloadUpcomingWorkouts();
                showNotification('Тренировка удалена!', 'success');
            } catch (err) {
                console.error('Ошибка при удалении:', err);
                showNotification('Ошибка при удалении', 'error');
            }
        });
    });

    document.querySelectorAll('.edit-schedule-btn').forEach(btn => {
        btn.addEventListener('click', async function (e) {
            e.preventDefault();
            const id = btn.dataset.id;
            try {
                const resp = await fetch(`/dashboard/schedule-data/${id}`, { signal: AbortSignal.timeout(10000) });
                if (!resp.ok) throw new Error('Ошибка загрузки данных');
                const data = await resp.json();
                document.getElementById('edit-schedule-id').value = data.id;
                document.getElementById('edit-activity').value = data.activity;
                document.getElementById('edit-scheduled_time').value = data.scheduled_time.slice(0, 16);
                document.getElementById('edit-schedule-modal').style.display = 'flex';
            } catch (err) {
                console.error('Ошибка загрузки данных:', err);
                showNotification('Ошибка загрузки данных', 'error');
            }
        });
    });

    const closeEditModal = document.getElementById('close-edit-modal');
    if (closeEditModal) {
        closeEditModal.addEventListener('click', function () {
            document.getElementById('edit-schedule-modal').style.display = 'none';
        });
    }

    const editScheduleForm = document.getElementById('edit-schedule-form');
    if (editScheduleForm) {
        editScheduleForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const id = document.getElementById('edit-schedule-id').value;
            const formData = new FormData(editScheduleForm);
            try {
                const resp = await fetch(`/dashboard/edit-schedule/${id}`, {
                    method: 'POST',
                    body: formData,
                    signal: AbortSignal.timeout(10000)
                });
                if (!resp.ok) throw new Error('Ошибка сохранения тренировки');
                document.getElementById('edit-schedule-modal').style.display = 'none';
                await reloadUpcomingWorkouts();
                showNotification('Тренировка обновлена!', 'success');
            } catch (err) {
                console.error('Ошибка при сохранении:', err);
                showNotification('Ошибка при сохранении', 'error');
            }
        });
    }
}

/**
 * Инициализация всплывающих подсказок
 */
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function () {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.top = rect.bottom + window.scrollY + 10 + 'px';
            tooltip.style.left = rect.left + window.scrollX + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';

            setTimeout(() => tooltip.classList.add('show'), 10);

            element.addEventListener('mouseleave', function onMouseLeave() {
                tooltip.classList.remove('show');
                setTimeout(() => document.body.removeChild(tooltip), 300);
                element.removeEventListener('mouseleave', onMouseLeave);
            });
        });
    });
}

/**
 * Инициализация анимаций появления элементов
 */
function initAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        animatedElements.forEach(element => observer.observe(element));
    } else {
        animatedElements.forEach(element => element.classList.add('visible'));
    }
}

/**
 * Инициализация мобильного меню
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navbarNav = document.querySelector('.navbar-nav');
    if (menuToggle && navbarNav) {
        menuToggle.addEventListener('click', function () {
            navbarNav.classList.toggle('show');
            this.classList.toggle('active');
        });
    }
}

/**
 * Инициализация переключателя темы
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.body.classList.add(currentTheme);
        themeToggle.checked = currentTheme === 'dark';

        themeToggle.addEventListener('change', function () {
            document.body.classList.toggle('dark', this.checked);
            document.body.classList.toggle('light', !this.checked);
            localStorage.setItem('theme', this.checked ? 'dark' : 'light');
        });
    }
}

/**
 * Инициализация графиков (заглушка для будущей реализации)
 */
function initCharts() {
    if (typeof Chart === 'undefined') return;
    Chart.defaults.font.family = "'Roboto', sans-serif";
    Chart.defaults.color = '#343A40';
    // Добавьте здесь код для создания графиков
}

/**
 * Валидация формы
 * @param {HTMLFormElement} form - Форма для валидации
 * @returns {boolean} - Результат валидации
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;

    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            markInvalid(input, 'Это поле обязательно для заполнения');
            isValid = false;
        } else if (input.type === 'email' && input.value.trim() && !validateEmail(input.value)) {
            markInvalid(input, 'Введите корректный email');
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
function validateEmail(email) {
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
        errorElement.remove();
    }
}

/**
 * Главная точка входа
 */
document.addEventListener('DOMContentLoaded', () => {
    // Инициализация стилей и UI
    initNotificationStyles();
    initUI();
    initTooltips();
    initAnimations();
    initMobileMenu();
    initThemeToggle();
    initCharts();

    // Привязка обработчиков
    bindProfileTabs();
    bindWorkoutCardHandlers();
    bindUpcomingWorkoutHandlers();
    bindAddScheduleForm();
    bindTimerHandlers();
    bindWorkoutFilters();
    bindWorkoutListHandlers();
    bindWorkoutCardActions();
    bindDeleteScheduleForms();

    // Динамическое обновление данных
    if (document.getElementById('workouts-list')) {
        updateWorkoutsList();
    }
    if (document.querySelector('.goals-list')) {
        updateGoalsProgress();
    }
    if (document.querySelector('#total-workouts')) {
        updateDashboardStats();
    }

    // Обработка кнопок профиля и целей
    document.querySelectorAll('.btn-primary, .btn-outline').forEach(btn => {
        if (btn.textContent.includes('Редактировать')) {
            btn.addEventListener('click', function () {
                const card = btn.closest('.card');
                if (card) {
                    card.querySelectorAll('input, select').forEach(input => {
                        input.disabled = false;
                    });
                    showNotification('Поля доступны для редактирования', 'info');
                }
            });
        } else if (btn.textContent.includes('Добавить цель')) {
            btn.addEventListener('click', function () {
                window.location.href = '/goals/add';
            });
        } else if (btn.textContent.includes('Сохранить настройки')) {
            btn.addEventListener('click', function () {
                showNotification('Настройки сохранены!', 'success');
            });
        }
    });

    // Валидация форм перед отправкой
    document.querySelectorAll('#add-schedule-form, #edit-schedule-form, #workout-form').forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!validateForm(form)) {
                e.preventDefault();
                showNotification('Пожалуйста, заполните все обязательные поля', 'error');
            }
        });
    });
});