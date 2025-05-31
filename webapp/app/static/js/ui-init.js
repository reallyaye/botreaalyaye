// UI INIT MODULE
function initUI() {
    initTooltips();
    initAnimations();
    initMobileMenu();
    initThemeToggle();
    if (typeof Chart !== 'undefined') initCharts();
}

export { initUI };
