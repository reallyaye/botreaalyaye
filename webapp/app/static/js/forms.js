// FORMS MODULE
function bindAddScheduleForm() {
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

export { bindAddScheduleForm };
