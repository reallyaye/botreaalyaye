import { initUI } from './ui-init.js';
import { bindProfileTabs } from './profile.js';
import { bindWorkoutCardHandlers } from './workouts.js';
import { bindUpcomingWorkoutHandlers } from './upcoming-workouts.js';
import { bindAddScheduleForm } from './forms.js';

// Основная точка входа для инициализации

document.addEventListener('DOMContentLoaded', () => {
    initUI();
    bindProfileTabs();
    bindWorkoutCardHandlers();
    bindUpcomingWorkoutHandlers();
    bindAddScheduleForm();
});
