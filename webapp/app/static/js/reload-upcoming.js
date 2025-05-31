// Динамическое обновление блока предстоящих тренировок
import { bindDeleteScheduleForms } from './upcoming-workouts.js';
import { fetchHtml } from './ajax-helpers.js';

async function reloadUpcomingWorkouts() {
    const html = await fetchHtml('/dashboard/upcoming-workouts');
    document.getElementById('upcoming-workouts-list').innerHTML = html;
    bindDeleteScheduleForms();
}

export { reloadUpcomingWorkouts };
