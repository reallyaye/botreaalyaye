// WORKOUTS MODULE (обычные)
import { showNotification } from './notifications.js';

function bindWorkoutCardHandlers() {
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

// Обновление списка тренировок через AJAX
async function updateWorkoutsList() {
    try {
        const resp = await fetch('/workouts/list-partial');
        if (resp.ok) {
            const html = await resp.text();
            document.getElementById('workouts-list').innerHTML = html;
            bindWorkoutCardHandlers();
        } else {
            showNotification('Ошибка при загрузке списка тренировок', 'error');
        }
    } catch (err) {
        console.error(err);
        showNotification('Ошибка при загрузке списка тренировок', 'error');
    }
}

// Обработчики для редактирования и удаления тренировок
function bindWorkoutListHandlers() {
    document.querySelectorAll('.edit-workout-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const id = btn.dataset.id;
            const resp = await fetch(`/workouts/edit/${id}`);
            if (resp.ok) {
                const w = await resp.json();
                document.getElementById('workout-modal-title').textContent = 'Редактировать тренировку';
                document.getElementById('workout-id').value = w.id;
                // Заполнение полей формы данными тренировки
            }
        });
    });
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

export { bindWorkoutCardHandlers, updateWorkoutsList, bindWorkoutListHandlers };
