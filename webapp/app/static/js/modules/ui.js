/**
 * UI Components Module
 * Contains functions for UI initialization and management
 */

/**
 * Initialize all UI components
 */
export function initUI() {
    initTooltips();
    initAnimations();
    initMobileMenu();
    initThemeToggle();
    if (typeof Chart !== 'undefined') initCharts();
}

/**
 * Инициализация всплывающих подсказок
 */
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
            tooltip.style.opacity = '1';
            
            const onMouseLeave = () => {
                tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (tooltip.parentNode) {
                        document.body.removeChild(tooltip);
                    }
                }, 300);
                this.removeEventListener('mouseleave', onMouseLeave);
            };
            
            this.addEventListener('mouseleave', onMouseLeave);
        });
    });
}

/**
 * Инициализация анимаций появления элементов
 */
function initAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    } else {
        // Fallback для браузеров без поддержки IntersectionObserver
        animatedElements.forEach(element => {
            element.classList.add('visible');
        });
    }
}

/**
 * Инициализация мобильного меню
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (menuToggle && navbarNav) {
        menuToggle.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
            this.classList.toggle('active');
        });
    }
}

/**
 * Инициализация переключателя темы
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    if (themeToggle) {
        // Установка начального состояния
        document.body.classList.add(currentTheme);
        themeToggle.checked = currentTheme === 'dark';
        
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.remove('light');
                document.body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark');
                document.body.classList.add('light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

/**
 * Инициализация графиков
 */
function initCharts() {
    // Общие настройки для всех графиков
    Chart.defaults.font.family = "'Roboto', sans-serif";
    Chart.defaults.color = '#343A40';
    
    // Цветовая схема для графиков
    const chartColors = {
        primary: '#4361EE',
        secondary: '#3A0CA3',
        accent: '#4CC9F0',
        success: '#28A745',
        warning: '#FFC107',
        danger: '#DC3545',
        info: '#17A2B8'
    };
}
