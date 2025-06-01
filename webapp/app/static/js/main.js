import { initUI } from './ui-init.js';
import { bindProfileTabs } from './profile.js';
import { bindWorkoutCardHandlers, updateWorkoutsList } from './workouts.js';
import { bindUpcomingWorkoutHandlers } from './upcoming-workouts.js';
import { bindAddScheduleForm } from './forms.js';
import { updateGoalsProgress } from './goals.js';

// Главная точка входа
document.addEventListener('DOMContentLoaded', () => {
    initUI();
    bindProfileTabs();
    bindWorkoutCardHandlers();
    bindUpcomingWorkoutHandlers();
    bindAddScheduleForm();
    
    // Автоматически подгружать список завершённых тренировок на вкладке "Тренировки"
    if (document.getElementById('workouts-list')) {
        updateWorkoutsList();
    }
    
    // Динамически обновлять прогресс по целям на dashboard
    if (document.querySelector('.goals-list')) {
        updateGoalsProgress();
    }
});

// --- AJAX HELPERS ---
async function fetchHtml(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.text();
    throw new Error('Ошибка загрузки');
}
async function fetchJson(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.json();
    throw new Error('Ошибка загрузки');
}



    // Инициализация всплывающих подсказок
    initTooltips();
    
    // Инициализация анимаций появления элементов
    initAnimations();
    
    // Обработка мобильного меню
    initMobileMenu();
    
    // Обработка темной темы
    initThemeToggle();
    
    // Инициализация графиков, если они есть на странице
    if (typeof Chart !== 'undefined') {
        initCharts();
    }

    // --- Кнопки "Начать" и "Подробнее" на тренировках ---
    // Только для обычных тренировок (не upcoming)
    document.querySelectorAll('.workout-card .workout-actions .btn-primary').forEach(btn => {
        btn.addEventListener('click', function() {
            const card = btn.closest('.workout-card');
            const title = card ? card.querySelector('.workout-title')?.textContent : '';
            if (title) {
                window.location.href = `/workouts/start?title=${encodeURIComponent(title)}`;
            } else {
                showNotification('Не удалось определить тренировку', 'error');
            }
        });
    });
    document.querySelectorAll('.workout-card .workout-actions .btn-outline').forEach(btn => {
        btn.addEventListener('click', function() {
            const card = btn.closest('.workout-card');
            const title = card ? card.querySelector('.workout-title')?.textContent : '';
            if (title) {
                window.location.href = `/workouts/details?title=${encodeURIComponent(title)}`;
            } else {
                showNotification('Не удалось определить тренировку', 'error');
            }
        });
    });

    // --- Фильтрация тренировок ---
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.textContent.trim();
            document.querySelectorAll('.workout-card').forEach(card => {
                if (filter === 'Все' || card.textContent.includes(filter)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // --- Табы профиля ---
    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.profile-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const tabName = tab.getAttribute('data-tab');
            document.querySelectorAll('.profile-tab-content').forEach(content => {
                content.classList.remove('active');
            });
            const activeContent = document.getElementById(`${tabName}-tab`);
            if (activeContent) activeContent.classList.add('active');
        });
    });

    // --- Кнопка "Редактировать" в профиле ---
    document.querySelectorAll('.btn-primary, .btn-outline').forEach(btn => {
        if (btn.textContent.includes('Редактировать')) {
            btn.addEventListener('click', function() {
                const card = btn.closest('.card');
                if (card) {
                    card.querySelectorAll('input, select').forEach(input => {
                        input.disabled = false;
                    });
                    showNotification('Поля доступны для редактирования', 'info');
                }
            });
        }
    });

    // --- Кнопка "Добавить цель" ---
    document.querySelectorAll('.btn-primary').forEach(btn => {
        if (btn.textContent.includes('Добавить цель')) {
            btn.addEventListener('click', function() {
                // Можно сделать переход на отдельную страницу или показать модальное окно
                window.location.href = '/goals/add';
            });
        }
    });

    // --- Кнопка "Сохранить настройки" ---
    document.querySelectorAll('.btn-primary').forEach(btn => {
        if (btn.textContent.includes('Сохранить настройки')) {
            btn.addEventListener('click', function() {
                // Можно реализовать отправку формы через AJAX
                showNotification('Настройки сохранены!', 'success');
            });
        }
    });

    // --- AJAX для предстоящих тренировок ---
    if (document.getElementById('add-schedule-form')) {
        document.getElementById('add-schedule-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const form = e.target;
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

    // --- Модальное окно редактирования тренировки ---
    document.body.addEventListener('click', async function(e) {
        if (e.target.classList.contains('edit-schedule-btn')) {
            const id = e.target.dataset.id;
            // Получаем данные тренировки через AJAX
            const resp = await fetch(`/dashboard/schedule-data/${id}`);
            if (resp.ok) {
                const data = await resp.json();
                document.getElementById('edit-schedule-id').value = data.id;
                document.getElementById('edit-activity').value = data.activity;
                document.getElementById('edit-scheduled_time').value = data.scheduled_time.slice(0,16);
                document.getElementById('edit-schedule-modal').style.display = 'flex';
            } else {
                showNotification('Ошибка загрузки данных', 'error');
            }
        }
        if (e.target.id === 'close-edit-modal') {
            document.getElementById('edit-schedule-modal').style.display = 'none';
        }
    });


    // --- Кнопка "Начать" с таймером ---
    document.body.addEventListener('click', async function(e) {
        if (e.target.classList.contains('start-schedule-btn')) {
            const id = e.target.dataset.id;
            // Получаем данные тренировки через AJAX
            const resp = await fetch(`/dashboard/schedule-data/${id}`);
            if (resp.ok) {
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
            } else {
                showNotification('Ошибка загрузки данных', 'error');
            }
        }
        if (e.target.id === 'close-timer-modal') {
            document.getElementById('start-timer-modal').style.display = 'none';
            if (timerInterval) clearInterval(timerInterval);
        }
    });



    // --- ВКЛАДКА ТРЕНИРОВКИ ---
    if (document.getElementById('workouts-list')) {
        // Фильтрация по типу
        document.querySelectorAll('.chip-filter').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.chip-filter').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const type = btn.dataset.type;
                document.querySelectorAll('.workout-history-card').forEach(card => {
                    if (type === 'all' || card.dataset.type.includes(type)) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
        // Поиск по названию
        document.getElementById('workout-search').addEventListener('input', function() {
            const val = this.value.toLowerCase();
            document.querySelectorAll('.workout-history-card').forEach(card => {
                const title = card.querySelector('div:nth-child(2) > div').textContent.toLowerCase();
                card.style.display = title.includes(val) ? '' : 'none';
            });
        });
        // Открытие модального окна для добавления
        document.getElementById('add-workout-btn').addEventListener('click', function() {
            document.getElementById('workout-modal-title').textContent = 'Добавить тренировку';
            document.getElementById('workout-form').reset();
            document.getElementById('workout-id').value = '';
            document.getElementById('workout-modal').style.display = 'flex';
        });
        // Закрытие модального окна
        document.getElementById('close-workout-modal').addEventListener('click', function() {
            document.getElementById('workout-modal').style.display = 'none';
        });
        // AJAX добавление/редактирование
        document.getElementById('workout-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const id = document.getElementById('workout-id').value;
            const formData = new FormData(e.target);
            let url = '/workouts/add';
            let method = 'POST';
            if (id) {
                url = `/workouts/edit/${id}`;
            }
            const resp = await fetch(url, { method, body: formData });
            if (resp.ok) {
                document.getElementById('workout-modal').style.display = 'none';
                await updateWorkoutsList();
                showNotification('Тренировка сохранена!', 'success');
            } else {
                showNotification('Ошибка при сохранении', 'error');
            }
        });
        // Первичная привязка
        bindWorkoutListHandlers();
    }


/**
 * Инициализация всплывающих подсказок
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = rect.bottom + window.scrollY + 10 + 'px';
            tooltip.style.left = rect.left + window.scrollX + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            
            setTimeout(() => {
                tooltip.classList.add('show');
            }, 10);
            
            this.addEventListener('mouseleave', function onMouseLeave() {
                tooltip.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(tooltip);
                }, 300);
                this.removeEventListener('mouseleave', onMouseLeave);
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
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    } else {
        // Fallback для браузеров без поддержки IntersectionObserver
        animatedElements.forEach(element => {
            element.classList.add('visible');
        });
    }
}

/**
 * Инициализация мобильного меню
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (menuToggle && navbarNav) {
        menuToggle.addEventListener('click', function() {
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
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    if (themeToggle) {
        // Установка начального состояния
        document.body.classList.add(currentTheme);
        themeToggle.checked = currentTheme === 'dark';
        
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.remove('light');
                document.body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark');
                document.body.classList.add('light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

/**
 * Инициализация графиков
 */
function initCharts() {
    // Общие настройки для всех графиков
    Chart.defaults.font.family = "'Roboto', sans-serif";
    Chart.defaults.color = '#343A40';
    
    // Цветовая схема для графиков
    const chartColors = {
        primary: '#4361EE',
        secondary: '#3A0CA3',
        accent: '#4CC9F0',
        success: '#28A745',
        warning: '#FFC107',
        danger: '#DC3545',
        info: '#17A2B8'
    };
}

/**
 * Отображение уведомления
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Длительность отображения в миллисекундах
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        </div>
        <div class="notification-content">
            <p>${message}</p>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        closeNotification(notification);
    });
    
    if (duration > 0) {
        setTimeout(() => {
            closeNotification(notification);
        }, duration);
    }
}

/**
 * Закрытие уведомления
 * @param {HTMLElement} notification - Элемент уведомления
 */
function closeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 300);
}

/**
 * Отправка AJAX запроса
 * @param {string} url - URL для запроса
 * @param {string} method - Метод запроса (GET, POST, PUT, DELETE)
 * @param {Object} data - Данные для отправки
 * @param {Function} callback - Функция обратного вызова при успешном запросе
 * @param {Function} errorCallback - Функция обратного вызова при ошибке
 */
function sendAjaxRequest(url, method, data, callback, errorCallback) {
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
                showNotification('Произошла ошибка при выполнении запроса', 'error');
            }
        }
    };
    
    xhr.onerror = function() {
        if (errorCallback) {
            errorCallback(0, 'Сетевая ошибка');
        } else {
            showNotification('Сетевая ошибка', 'error');
        }
    };
    
    xhr.send(JSON.stringify(data));
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
        errorElement.parentNode.removeChild(errorElement);
    }
}

async function updateWorkoutsList() {
    const resp = await fetch('/workouts/list-partial');
    if (resp.ok) {
        const html = await resp.text();
        document.getElementById('workouts-list').innerHTML = html;
        bindWorkoutListHandlers();
    }
}

function bindWorkoutListHandlers() {
    // Открытие модального окна для редактирования
    document.querySelectorAll('.edit-workout-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const id = btn.dataset.id;
            const resp = await fetch(`/workouts/edit/${id}`);
            if (resp.ok) {
                const w = await resp.json();
                document.getElementById('workout-modal-title').textContent = 'Редактировать тренировку';
                document.getElementById('workout-id').value = w.id;
                document.getElementById('workout-activity').value = w.activity;
                document.getElementById('workout-intensity').value = w.intensity;
                document.getElementById('workout-duration').value = w.duration;
                document.getElementById('workout-comment').value = w.comment || '';
                document.getElementById('workout-modal').style.display = 'flex';
            } else {
                showNotification('Ошибка загрузки тренировки', 'error');
            }
        });
    });
    // Удаление тренировки
    document.querySelectorAll('.delete-workout-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            if (!confirm('Удалить тренировку?')) return;
            const id = btn.dataset.id;
            const resp = await fetch(`/workouts/delete/${id}`, { method: 'POST' });
            if (resp.ok) {
                await updateWorkoutsList();
                showNotification('Тренировка удалена!', 'success');
            } else {
                showNotification('Ошибка при удалении', 'error');
            }
        });
    });
}

// === Динамическое обновление блока предстоящих тренировок ===
// async function reloadUpcomingWorkouts() {
//     const resp = await fetch('/dashboard/upcoming-workouts');
//     if (resp.ok) {
//         const html = await resp.text();
//         document.getElementById('upcoming-workouts-list').innerHTML = html;
//         bindDeleteScheduleForms();
//     }
// }

// Переинициализация обработчиков удаления
// function bindDeleteScheduleForms() {
//     document.querySelectorAll('.delete-schedule-form').forEach(form => {
//         form.onsubmit = async function(e) {
//             e.preventDefault();
//             const id = form.dataset.id;
//             if (!confirm('Удалить предстоящую тренировку?')) return;
//             const resp = await fetch(`/dashboard/delete-schedule/${id}`, { method: 'POST' });
//             if (resp.ok) {
//                 await reloadUpcomingWorkouts();
//                 showNotification('Тренировка удалена!', 'success');
//             } else {
//                 showNotification('Ошибка при удалении', 'error');
//             }
//         };
//     });
//     // Обработчик для кнопки "Изменить" предстоящей тренировки
//     document.querySelectorAll('.edit-schedule-btn').forEach(btn => {
//         btn.onclick = async function(e) {
//             e.preventDefault();
//             const id = btn.dataset.id;
//             // Получаем данные тренировки через AJAX
//             const resp = await fetch(`/dashboard/schedule-data/${id}`);
//             if (resp.ok) {
//                 const data = await resp.json();
//                 document.getElementById('edit-schedule-id').value = data.id;
//                 document.getElementById('edit-activity').value = data.activity;
//                 document.getElementById('edit-scheduled_time').value = data.scheduled_time.slice(0,16);
//                 document.getElementById('edit-schedule-modal').style.display = 'flex';
//             } else {
//                 showNotification('Ошибка загрузки данных', 'error');
//             }
//         };
//     });
//     // Обработчик закрытия модального окна редактирования
//     const closeEditModal = document.getElementById('close-edit-modal');
//     if (closeEditModal) {
//         closeEditModal.onclick = function() {
//             document.getElementById('edit-schedule-modal').style.display = 'none';
//         };
//     }
//     // Обработчик отправки формы редактирования
//     const editScheduleForm = document.getElementById('edit-schedule-form');
//     if (editScheduleForm) {
//         editScheduleForm.onsubmit = async function(e) {
//             e.preventDefault();
//             const id = document.getElementById('edit-schedule-id').value;
//             const formData = new FormData(editScheduleForm);
//             const resp = await fetch(`/dashboard/edit-schedule/${id}`, {
//                 method: 'POST',
//                 body: formData
//             });
//             if (resp.redirected || resp.ok) {
//                 document.getElementById('edit-schedule-modal').style.display = 'none';
//                 await reloadUpcomingWorkouts();
//                 showNotification('Тренировка обновлена!', 'success');
//             } else {
//                 showNotification('Ошибка при сохранении', 'error');
//             }
//         };
//     }
// }

// --- Простое уведомление ---
function showNotification(msg, type) {
    let n = document.createElement('div');
    n.className = 'custom-toast ' + (type === 'success' ? 'toast-success' : 'toast-error');
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(() => { n.classList.add('show'); }, 10);
    setTimeout(() => { n.classList.remove('show'); setTimeout(()=>n.remove(), 300); }, 2500);
}

// --- Стили для уведомлений ---
if (!document.getElementById('custom-toast-style')) {
    const style = document.createElement('style');
    style.id = 'custom-toast-style';
    style.innerHTML = `.custom-toast {position:fixed;top:30px;right:30px;z-index:9999;padding:16px 28px;border-radius:8px;font-size:1.1em;box-shadow:0 2px 12px rgba(0,0,0,0.12);opacity:0;pointer-events:none;transition:opacity .3s,transform .3s;transform:translateY(-20px);} .custom-toast.show {opacity:1;pointer-events:auto;transform:translateY(0);} .toast-success {background:#4caf50;color:#fff;} .toast-error {background:#e53935;color:#fff;}`;
    document.head.appendChild(style);
}

let timerInterval = null;
let timerStart = null;
let timerActivity = '';
let timerScheduleId = null;

async function updateDashboardStats() {
    const resp = await fetch('/dashboard/stats-json');
    if (resp.ok) {
        const stats = await resp.json();
        document.getElementById('total-workouts').textContent = stats.total_workouts;
        document.getElementById('total-minutes').textContent = stats.total_minutes;
        document.getElementById('total-calories').textContent = stats.total_calories;
        document.getElementById('achievements-count').textContent = stats.achievements_count;
    }
}

// --- Обработчики для редактирования расписания ---
function bindEditScheduleHandlers() {
    // Кнопки "Изменить"
    document.querySelectorAll('.edit-schedule-btn').forEach(btn => {
        btn.onclick = async function(e) {
            e.preventDefault();
            const id = btn.dataset.id;
            const resp = await fetch(`/dashboard/schedule-data/${id}`);
            if (resp.ok) {
                const data = await resp.json();
                document.getElementById('edit-schedule-id').value = data.id;
                document.getElementById('edit-activity').value = data.activity;
                document.getElementById('edit-scheduled_time').value = data.scheduled_time.slice(0,16);
                document.getElementById('edit-schedule-modal').style.display = 'flex';
            } else {
                showNotification('Ошибка загрузки данных', 'error');
            }
        };
    });

    // Закрытие модального окна
    const closeEditModal = document.getElementById('close-edit-modal');
    if (closeEditModal) {
        closeEditModal.onclick = function() {
            document.getElementById('edit-schedule-modal').style.display = 'none';
        };
    }

    // Отправка формы редактирования
    const editScheduleForm = document.getElementById('edit-schedule-form');
    if (editScheduleForm) {
        editScheduleForm.onsubmit = async function(e) {
            e.preventDefault();
            const id = document.getElementById('edit-schedule-id').value;
            const formData = new FormData(editScheduleForm);
            const resp = await fetch(`/dashboard/edit-schedule/${id}`, {
                method: 'POST',
                body: formData
            });
            if (resp.redirected || resp.ok) {
                document.getElementById('edit-schedule-modal').style.display = 'none';
                await reloadUpcomingWorkouts();
                showNotification('Тренировка обновлена!', 'success');
            } else {
                showNotification('Ошибка при сохранении', 'error');
            }
        };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    bindEditScheduleHandlers();
});
