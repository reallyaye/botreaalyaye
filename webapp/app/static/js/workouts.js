// WORKOUTS MODULE (обычные)
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

export { bindWorkoutCardHandlers };
