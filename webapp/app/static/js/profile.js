// PROFILE MODULE
import { showNotification } from './notifications.js';
import { updateGoalsProgress } from './goals.js';

function bindProfileTabs() {
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

    // --- Профиль: редактирование и сохранение ---
    bindPersonalDataForm();
    
    // --- Добавление новой цели ---
    bindGoalsForm();
    
    // --- Настройки аккаунта ---
    bindAccountSettingsForm();
    
    // --- Безопасность (смена пароля) ---
    bindSecurityForm();
    
    // --- Двухфакторная аутентификация ---
    bindTwoFactorAuth();
    
    // --- Опасная зона ---
    bindDangerZone();
}

// Обработчик формы личных данных
function bindPersonalDataForm() {
    const editBtn = document.getElementById('editProfileBtn');
    const profileForm = document.getElementById('profile-form');
    
    if (editBtn && profileForm) {
        editBtn.addEventListener('click', function() {
            profileForm.querySelectorAll('input, select, textarea').forEach(el => {
                if (el.type !== 'hidden') el.disabled = false;
            });
            editBtn.style.display = 'none';
            const saveBtn = profileForm.querySelector('.btn-primary[type="submit"]');
            if (saveBtn) saveBtn.style.display = '';
        });
        
        // Кнопка "Сохранить" (submit)
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(profileForm);
            const resp = await fetch(profileForm.action || '/profile/update', {
                method: 'POST',
                body: formData
            });
            if (resp.ok) {
                showNotification('Профиль обновлён!', 'success');
                // Заблокировать поля обратно
                profileForm.querySelectorAll('input, select, textarea').forEach(el => {
                    if (el.type !== 'hidden') el.disabled = true;
                });
                editBtn.style.display = '';
                const saveBtn = profileForm.querySelector('.btn-primary[type="submit"]');
                if (saveBtn) saveBtn.style.display = 'none';
                // Можно обновить имя/email/аватар на странице без перезагрузки (если нужно)
            } else {
                showNotification('Ошибка при сохранении профиля', 'error');
            }
        });
        
        // Скрыть кнопку "Сохранить" по умолчанию
        const saveBtn = profileForm.querySelector('.btn-primary[type="submit"]');
        if (saveBtn) saveBtn.style.display = 'none';
    }
}

// Обработчик формы добавления цели
function bindGoalsForm() {
    // Найти карточку формы добавления цели по уникальному тексту кнопки или классу
    const card = document.querySelector('#goals-tab .card');
    if (!card) return;

    // Кнопка добавления цели
    const addGoalBtn = card.querySelector('button.btn-primary, button[type="submit"]');
    if (!addGoalBtn) return;

    addGoalBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        // Получаем значения полей
        const typeInput = card.querySelector('select');
        const valueInput = card.querySelector('input[type="number"]');
        const dateInput = card.querySelector('input[type="date"], input[type="text"][name*="date"], input[type="text"][placeholder*="достижения"]');
        const priorityInput = card.querySelectorAll('select')[1] || card.querySelector('select[name*="priority"]');

        let valid = true;
        // Очистить прошлые ошибки
        [typeInput, valueInput, dateInput, priorityInput].forEach(input => { if(input) clearInvalid(input); });

        // Проверки
        if (!typeInput || !typeInput.value) {
            markInvalid(typeInput, 'Выберите тип цели');
            valid = false;
        }
        if (!valueInput || !valueInput.value || isNaN(valueInput.value) || Number(valueInput.value) <= 0) {
            markInvalid(valueInput, 'Введите корректное значение');
            valid = false;
        }
        if (!dateInput || !dateInput.value) {
            markInvalid(dateInput, 'Укажите срок достижения');
            valid = false;
        } else {
            // Проверка, что дата в будущем
            let userDate = dateInput.value;
            // Преобразуем дату, если она в формате DD.MM.YYYY
            if (/\d{2}\.\d{2}\.\d{4}/.test(userDate)) {
                const [d, m, y] = userDate.split('.');
                userDate = `${y}-${m}-${d}`;
            }
            const dateObj = new Date(userDate);
            const now = new Date();
            now.setHours(0,0,0,0);
            if (isNaN(dateObj.getTime()) || dateObj < now) {
                markInvalid(dateInput, 'Дата должна быть в будущем');
                valid = false;
            }
        }
        if (!priorityInput || !priorityInput.value) {
            markInvalid(priorityInput, 'Выберите приоритет');
            valid = false;
        }
        if (!valid) {
            showNotification('Проверьте правильность заполнения полей', 'error');
            return;
        }
        // Собираем данные
        const payload = {
            type: typeInput.value,
            value: valueInput.value,
            due_date: dateInput.value,
            priority: priorityInput.value
        };
        try {
            const resp = await fetch('/goals/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (resp.ok) {
                showNotification('Цель добавлена!', 'success');
                // Очистить поля
                [typeInput, valueInput, dateInput, priorityInput].forEach(input => {
                    if (input.tagName === 'SELECT') input.selectedIndex = 0;
                    else input.value = '';
                    clearInvalid(input);
                });
                // Обновить список целей
                if (typeof updateGoalsProgress === 'function') updateGoalsProgress();
            } else {
                showNotification('Ошибка при добавлении цели', 'error');
            }
        } catch (err) {
            showNotification('Ошибка при добавлении цели', 'error');
            console.error(err);
        }
    });
}

// --- ДОБАВЛЕНО: AJAX-работа с целями ---
document.addEventListener('DOMContentLoaded', function() {
  bindGoalsAjax();
});

function bindGoalsAjax() {
  const addGoalForm = document.getElementById('add-goal-form');
  if (addGoalForm) {
    addGoalForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const formData = new FormData(addGoalForm);
      try {
        const response = await fetch('/goals/add-json', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
          showNotification(data.message, 'success');
          addGoalForm.reset();
          await refreshGoalsList();
        } else {
          showNotification(data.message || 'Ошибка!', 'error');
        }
      } catch (error) {
        showNotification('Ошибка сети или сервера при добавлении цели.', 'error');
      }
    });
  }
  // Делегирование для кнопок удаления
  document.getElementById('goals-list-container').addEventListener('click', async function(e) {
    if (e.target.classList.contains('delete-goal-btn')) {
      const goalId = e.target.dataset.goalId;
      const csrfToken = document.querySelector('input[name="csrf_token"]').value;
      if (!confirm('Удалить эту цель?')) return;
      const formData = new FormData();
      formData.append('csrf_token', csrfToken);
      try {
        const response = await fetch(`/goals/delete-json/${goalId}`, {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
          showNotification(data.message, 'success');
          await refreshGoalsList();
        } else {
          showNotification(data.message || 'Ошибка!', 'error');
        }
      } catch (error) {
        showNotification('Ошибка сети или сервера при удалении цели.', 'error');
      }
    }
  });
}

async function refreshGoalsList() {
  const container = document.getElementById('goals-list-container');
  if (!container) return;
  const response = await fetch('/goals/list');
  const html = await response.text();
  container.innerHTML = html;
}

// Обработчик формы настроек аккаунта
function bindAccountSettingsForm() {
    const settingsBtn = document.querySelector('#settings-tab .btn-primary');
    
    if (settingsBtn) {
        settingsBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            const card = this.closest('.card');
            const formData = new FormData();
            
            // Собираем данные из формы
            const language = card.querySelector('select').value;
            const timezone = card.querySelector('select:nth-of-type(2)').value;
            const units = card.querySelector('input[name="units"]:checked').nextElementSibling.textContent.includes('Метрические') ? 'metric' : 'imperial';
            const theme = card.querySelector('input[name="theme"]:checked').nextElementSibling.textContent.trim();
            
            formData.append('language', language);
            formData.append('timezone', timezone);
            formData.append('units', units);
            formData.append('theme', theme);
            
            try {
                const resp = await fetch('/profile/settings', {
                    method: 'POST',
                    body: formData
                });
                
                if (resp.ok) {
                    showNotification('Настройки сохранены!', 'success');
                    // Применить настройки темы без перезагрузки
                    if (theme === 'Светлая') {
                        document.body.classList.remove('dark');
                        document.body.classList.add('light');
                        localStorage.setItem('theme', 'light');
                    } else if (theme === 'Темная') {
                        document.body.classList.remove('light');
                        document.body.classList.add('dark');
                        localStorage.setItem('theme', 'dark');
                    } else if (theme === 'Системная') {
                        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                        document.body.classList.remove(prefersDark ? 'light' : 'dark');
                        document.body.classList.add(prefersDark ? 'dark' : 'light');
                        localStorage.removeItem('theme');
                    }
                } else {
                    showNotification('Ошибка при сохранении настроек', 'error');
                }
            } catch (err) {
                showNotification('Ошибка при сохранении настроек', 'error');
                console.error(err);
            }
        });
    }
}

// Обработчик формы безопасности (смена пароля)
function bindSecurityForm() {
    const securityBtn = document.querySelector('#settings-tab .card:nth-of-type(2) .btn-primary');
    
    if (securityBtn) {
        securityBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            const card = this.closest('.card');
            const formData = new FormData();
            
            const currentPassword = card.querySelector('input[type="password"]:nth-of-type(1)').value;
            const newPassword = card.querySelector('input[type="password"]:nth-of-type(2)').value;
            const confirmPassword = card.querySelector('input[type="password"]:nth-of-type(3)').value;
            
            if (newPassword !== confirmPassword) {
                showNotification('Пароли не совпадают', 'error');
                return;
            }
            
            formData.append('current_password', currentPassword);
            formData.append('new_password', newPassword);
            
            try {
                const resp = await fetch('/profile/change-password', {
                    method: 'POST',
                    body: formData
                });
                
                if (resp.ok) {
                    showNotification('Пароль успешно изменён!', 'success');
                    // Очистка полей ввода
                    card.querySelectorAll('input[type="password"]').forEach(input => input.value = '');
                } else {
                    const data = await resp.json();
                    showNotification(data.error || 'Ошибка при смене пароля', 'error');
                }
            } catch (err) {
                showNotification('Ошибка при смене пароля', 'error');
                console.error(err);
            }
        });
    }
}

// Обработчик двухфакторной аутентификации
function bindTwoFactorAuth() {
    const twoFactorToggle = document.querySelector('#twoFactorAuth');
    
    if (twoFactorToggle) {
        twoFactorToggle.addEventListener('change', async function() {
            const isEnabled = this.checked;
            const label = this.parentElement.querySelector('.toggle-label');
            
            try {
                const resp = await fetch('/profile/two-factor-auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ enabled: isEnabled })
                });
                
                if (resp.ok) {
                    label.textContent = isEnabled ? 'Включена' : 'Выключена';
                    showNotification(`Двухфакторная аутентификация ${isEnabled ? 'включена' : 'выключена'}`, 'success');
                } else {
                    // Восстановить предыдущее состояние переключателя
                    this.checked = !isEnabled;
                    label.textContent = !isEnabled ? 'Включена' : 'Выключена';
                    showNotification('Ошибка при изменении настроек аутентификации', 'error');
                }
            } catch (err) {
                // Восстановить предыдущее состояние переключателя
                this.checked = !isEnabled;
                label.textContent = !isEnabled ? 'Включена' : 'Выключена';
                showNotification('Ошибка при изменении настроек аутентификации', 'error');
                console.error(err);
            }
        });
    }
}

// Обработчики опасной зоны
function bindDangerZone() {
    // Удаление данных тренировок
    const deleteWorkoutsBtn = document.querySelector('.danger-zone .danger-action:nth-of-type(1) .btn-danger');
    
    if (deleteWorkoutsBtn) {
        deleteWorkoutsBtn.addEventListener('click', async function() {
            if (!confirm('Вы уверены, что хотите удалить все данные тренировок? Это действие необратимо.')) {
                return;
            }
            
            try {
                const resp = await fetch('/profile/delete-workouts', {
                    method: 'POST'
                });
                
                if (resp.ok) {
                    showNotification('Все данные тренировок удалены', 'success');
                } else {
                    showNotification('Ошибка при удалении данных', 'error');
                }
            } catch (err) {
                showNotification('Ошибка при удалении данных', 'error');
                console.error(err);
            }
        });
    }
    
    // Удаление аккаунта
    const deleteAccountBtn = document.querySelector('.danger-zone .danger-action:nth-of-type(2) .btn-danger');
    
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', async function() {
            if (!confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие необратимо и приведет к потере всех данных.')) {
                return;
            }
            
            try {
                const resp = await fetch('/profile/delete-account', {
                    method: 'POST'
                });
                
                if (resp.ok) {
                    showNotification('Аккаунт удален', 'success');
                    // Редирект на главную после короткой паузы
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } else {
                    showNotification('Ошибка при удалении аккаунта', 'error');
                }
            } catch (err) {
                showNotification('Ошибка при удалении аккаунта', 'error');
                console.error(err);
            }
        });
    }
}

export { bindProfileTabs };
