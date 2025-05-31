/**
 * Main entry point for the application
 * Imports and initializes all modules
 */

// Import modules
import { initUI } from './modules/ui.js';
import { bindProfileTabs } from './modules/profile.js';
import { bindWorkoutCardHandlers, bindWorkoutListHandlers } from './modules/workouts.js';
import { bindUpcomingWorkoutHandlers } from './modules/upcoming-workouts.js';
import { bindAddScheduleForm } from './modules/forms.js';
import { showNotification, initNotificationStyles } from './modules/notifications.js';
import { initTimer } from './modules/timer.js';
import { updateDashboardStats } from './modules/ajax.js';

// Главная точка входа
document.addEventListener('DOMContentLoaded', () => {
    // Initialize notification styles
    initNotificationStyles();
    
    // Initialize UI components
    initUI();
    
    // Bind event handlers
    bindProfileTabs();
    bindWorkoutCardHandlers();
    bindUpcomingWorkoutHandlers();
    bindAddScheduleForm();
    
    // Initialize timer functionality
    initTimer();
    
    // Update dashboard stats if on dashboard page
    if (document.getElementById('total-workouts')) {
        updateDashboardStats();
    }
    
    // Initialize workout list handlers if on workouts page
    if (document.getElementById('workouts-list')) {
        bindWorkoutListHandlers();
    }
});
