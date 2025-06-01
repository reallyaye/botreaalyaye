// UI INIT MODULE
import { initTooltips } from './tooltips.js';

// UI Initialization Functions
function initAnimations() {
    document.querySelectorAll('.fade-in').forEach(el => {
        el.classList.add('visible');
    });
}

function initMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const sideMenu = document.querySelector('.side-menu');
    
    if (mobileMenuBtn && sideMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            sideMenu.classList.toggle('open');
        });
    }
}

function initThemeToggle() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.remove('light', 'dark');
        document.body.classList.add(savedTheme);
    } else {
        // Определение системной темы
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.body.classList.add(prefersDark ? 'dark' : 'light');
    }
}

function initCharts() {
    const ctx = document.getElementById('workoutsChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                datasets: [{
                    label: 'Количество тренировок',
                    data: [2, 3, 1, 0, 2, 4, 1],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            }
        });
    }
}

function initUI() {
    initTooltips();
    initAnimations();
    initMobileMenu();
    initThemeToggle();
    if (typeof Chart !== 'undefined') initCharts();
}

export { initUI };
