/**
 * Upcoming Workouts Module
 * Contains functions for upcoming workout management
 */

import { showNotification } from './notifications.js';

/**
 * Bind upcoming workout handlers
 */
export function bindUpcomingWorkoutHandlers() {
    bindDeleteScheduleForms();
    // Переинициализировать после загрузки блока
    setTimeout(() => {
        if (document.getElementById('upcoming-workouts-list')) {
            bindDeleteScheduleForms();
        }
    }, 100);
}

/**
 * Bind delete schedule forms
 */
export function bindDeleteScheduleForms() {
    document.querySelectorAll('.delete-schedule-form').forEach(form => {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const id = form.dataset.id;
            if (!confirm('Удалить предстоящую тренировку?')) return;
            const resp = await fetch(`/dashboard/delete-schedule/${id}`, { method: 'POST' });
            if (resp.ok) {
                await reloadUpcomingWorkouts();
                showNotification('Тренировка удалена!', 'success');
            } else {
                showNotification('Ошибка при удалении', 'error');
            }
        };
    });
    // "Изменить" предстоящую тренировку
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

/**
 * Reload upcoming workouts
 */
export async function reloadUpcomingWorkouts() {
    const html = await fetchHtml('/dashboard/upcoming-workouts');
    document.getElementById('upcoming-workouts-list').innerHTML = html;
    bindDeleteScheduleForms();
}

/**
 * Update upcoming workouts
 */
export async function updateUpcomingWorkouts() {
    const resp = await fetch('/dashboard/upcoming-workouts');
    if (resp.ok) {
        const html = await resp.text();
        document.getElementById('upcoming-workouts-container').innerHTML = html;
        bindDeleteScheduleForms();
    }
}

/**
 * Fetch HTML content
 */
async function fetchHtml(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.text();
    throw new Error('Ошибка загрузки');
}
