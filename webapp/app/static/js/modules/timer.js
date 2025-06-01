/**
 * Timer Module
 * Contains functions for timer functionality
 */

import { showNotification } from './notifications.js';

// Timer variables
let timerInterval = null;
let timerStart = null;
let timerActivity = '';
let timerScheduleId = null;

/**
 * Initialize timer functionality
 */
export function initTimer() {
    // Handle timer start button
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
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }
    });
}

/**
 * Stop timer
 */
export function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}
