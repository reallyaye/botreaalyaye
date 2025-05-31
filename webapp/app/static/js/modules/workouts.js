/**
 * Workouts Module
 * Contains functions for workout card management
 */

import { showNotification } from './notifications.js';

/**
 * Bind workout card handlers
 */
export function bindWorkoutCardHandlers() {
    // "Начать" и "Подробнее" только для обычных тренировок
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
    // Фильтрация
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
}

/**
 * Bind workout list handlers
 */
export function bindWorkoutListHandlers() {
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

/**
 * Update workouts list
 */
async function updateWorkoutsList() {
    const resp = await fetch('/workouts/list-partial');
    if (resp.ok) {
        const html = await resp.text();
        document.getElementById('workouts-list').innerHTML = html;
        bindWorkoutListHandlers();
    }
}
