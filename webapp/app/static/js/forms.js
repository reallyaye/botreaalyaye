// FORMS MODULE
import { showNotification } from './notifications.js';
import { reloadUpcomingWorkouts } from './upcoming-workouts.js';

function bindAddScheduleForm() {
    const form = document.getElementById('add-schedule-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (response.ok) {
                await reloadUpcomingWorkouts();
                showNotification('Тренировка добавлена!', 'success');
                form.reset();
            } else {
                let errorMsg = 'Ошибка при добавлении тренировки';
                try {
                    const data = await response.json();
                    if (data && data.error === 'invalid_datetime') {
                        errorMsg = 'Некорректная дата/время';
                    }
                } catch {}
                showNotification(errorMsg, 'error');
            }
        });
    }
}

export { bindAddScheduleForm };
