// GOALS MODULE
import { showNotification } from './notifications.js';

async function updateGoalsProgress() {
    try {
        const resp = await fetch('/dashboard/goals-json');
        if (!resp.ok) throw new Error('Ошибка загрузки целей');
        const goals = await resp.json();
        const container = document.querySelector('.goals-list');
        if (!goals.length) {
            container.innerHTML = '<div style="color: var(--text-muted); padding: 24px; text-align: center;">Нет активных целей</div>';
            return;
        }
        container.innerHTML = goals.map(goal => `
            <a href="/goals" class="goal-item" style="text-decoration:none; color:inherit; cursor:pointer;">
                <div class="goal-info">
                    <div class="goal-name">${goal.goal_type.charAt(0).toUpperCase() + goal.goal_type.slice(1)}</div>
                    <div class="goal-value">${goal.current_value}/${goal.target_value}
                        ${goal.goal_type === 'duration' ? ' мин' : goal.goal_type === 'calories' ? ' ккал' : goal.goal_type === 'workouts' ? ' трен.' : ''}
                    </div>
                </div>
                <div class="goal-progress-bg">
                    <div class="goal-progress-fill" style="width: ${Math.round(goal.progress)}%;"></div>
                </div>
            </a>
        `).join('');
    } catch (e) {
        const container = document.querySelector('.goals-list');
        if (container) container.innerHTML = '<div style="color: var(--danger); padding: 24px; text-align: center;">Ошибка загрузки целей</div>';
    }
}

export { updateGoalsProgress };
