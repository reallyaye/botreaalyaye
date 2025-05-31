/**
 * Profile Module
 * Contains functions for profile tab management
 */

/**
 * Bind profile tab functionality
 */
export function bindProfileTabs() {
    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.profile-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const tabName = tab.getAttribute('data-tab');
            document.querySelectorAll('.profile-tab-content').forEach(content => {
                content.classList.remove('active');
            });
            const activeContent = document.getElementById(`${tabName}-tab`);
            if (activeContent) activeContent.classList.add('active');
        });
    });
    
    // --- Кнопка "Редактировать" в профиле ---
    document.querySelectorAll('.btn-primary, .btn-outline').forEach(btn => {
        if (btn.textContent.includes('Редактировать')) {
            btn.addEventListener('click', function() {
                const card = btn.closest('.card');
                if (card) {
                    card.querySelectorAll('input, select').forEach(input => {
                        input.disabled = false;
                    });
                    // Import will be added in main.js
                    // showNotification('Поля доступны для редактирования', 'info');
                }
            });
        }
    });
    
    // --- Кнопка "Добавить цель" ---
    document.querySelectorAll('.btn-primary').forEach(btn => {
        if (btn.textContent.includes('Добавить цель')) {
            btn.addEventListener('click', function() {
                // Можно сделать переход на отдельную страницу или показать модальное окно
                window.location.href = '/goals/add';
            });
        }
    });
    
    // --- Кнопка "Сохранить настройки" ---
    document.querySelectorAll('.btn-primary').forEach(btn => {
        if (btn.textContent.includes('Сохранить настройки')) {
            btn.addEventListener('click', function() {
                // Можно реализовать отправку формы через AJAX
                // Import will be added in main.js
                // showNotification('Настройки сохранены!', 'success');
            });
        }
    });
}
