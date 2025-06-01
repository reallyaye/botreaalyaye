/**
 * Notifications Module
 * Contains functions for displaying notifications to the user
 */

/**
 * Отображение уведомления
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Длительность отображения в миллисекундах
 */
export function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        </div>
        <div class="notification-content">
            <p>${message}</p>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        closeNotification(notification);
    });
    
    if (duration > 0) {
        setTimeout(() => {
            closeNotification(notification);
        }, duration);
    }
}

/**
 * Закрытие уведомления
 * @param {HTMLElement} notification - Элемент уведомления
 */
function closeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 300);
}

/**
 * Simple toast notification
 * @param {string} msg - Message text
 * @param {string} type - Notification type (success, error)
 */
export function showSimpleNotification(msg, type) {
    let n = document.createElement('div');
    n.className = 'custom-toast ' + (type === 'success' ? 'toast-success' : 'toast-error');
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(() => { n.classList.add('show'); }, 10);
    setTimeout(() => { n.classList.remove('show'); setTimeout(()=>n.remove(), 300); }, 2500);
}

// Add toast styles if not already present
export function initNotificationStyles() {
    if (!document.getElementById('custom-toast-style')) {
        const style = document.createElement('style');
        style.id = 'custom-toast-style';
        style.innerHTML = `.custom-toast {position:fixed;top:30px;right:30px;z-index:9999;padding:16px 28px;border-radius:8px;font-size:1.1em;box-shadow:0 2px 12px rgba(0,0,0,0.12);opacity:0;pointer-events:none;transition:opacity .3s,transform .3s;transform:translateY(-20px);} .custom-toast.show {opacity:1;pointer-events:auto;transform:translateY(0);} .toast-success {background:#4caf50;color:#fff;} .toast-error {background:#e53935;color:#fff;}`;
        document.head.appendChild(style);
    }
}
