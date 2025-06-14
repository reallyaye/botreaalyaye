// Закрытие уведомлений
document.querySelectorAll('.alert').forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            alert.classList.add('hide');
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    }
    
    // Автоматическое закрытие через 5 секунд
    setTimeout(() => {
        if (alert && !alert.classList.contains('hide')) {
            alert.classList.add('hide');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }
    }, 5000);
});

// Функция для создания уведомлений
function createAlert(message, type = 'info', dismissible = true) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} ${dismissible ? 'alert-dismissible fade show' : ''}`;
    alert.setAttribute('role', 'alert');
    
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    alert.appendChild(messageSpan);
    
    if (dismissible) {
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'alert-close';
        closeBtn.setAttribute('aria-label', 'Закрыть');
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        
        closeBtn.addEventListener('click', () => {
            alert.classList.add('hide');
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
        
        alert.appendChild(closeBtn);
    }
    
    // Добавление уведомления в контейнер
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    } else {
        document.body.insertBefore(alert, document.body.firstChild);
    }
    
    // Автоматическое закрытие через 5 секунд
    if (dismissible) {
        setTimeout(() => {
            alert.classList.add('hide');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    }
    
    return alert;
}

// Глобальные функции для создания уведомлений разных типов
window.showSuccess = (message, dismissible = true) => {
    return createAlert(message, 'success', dismissible);
};

window.showError = (message, dismissible = true) => {
    return createAlert(message, 'danger', dismissible);
};

window.showWarning = (message, dismissible = true) => {
    return createAlert(message, 'warning', dismissible);
};

window.showInfo = (message, dismissible = true) => {
    return createAlert(message, 'info', dismissible);
}; 