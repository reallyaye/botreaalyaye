/**
 * NOVIII Fitness Bot - Telegram UI Helper
 * Этот файл содержит функции для стилизации интерфейса Telegram-бота
 */

// Константы для цветовой схемы
const COLORS = {
  primary: '#4361EE',
  secondary: '#3A0CA3',
  tertiary: '#4CC9F0',
  success: '#4DCCBD',
  warning: '#F72585',
  background: '#17212B', // Темный фон Telegram
  cardBg: '#242F3D',     // Фон карточек в Telegram
  textLight: '#FFFFFF',
  textMuted: '#8A96A3'
};

/**
 * Создает стилизованную кнопку для Telegram-бота
 * @param {string} text - Текст кнопки
 * @param {string} color - Цвет кнопки (из COLORS)
 * @param {string} callback - Callback данные
 * @returns {Object} - Объект кнопки для Telegram API
 */
function createButton(text, color = COLORS.primary, callback = '') {
  return {
    text: text,
    callback_data: callback,
    // Дополнительные параметры для стилизации через Telegram Bot API
  };
}

/**
 * Создает карточку тренировки для Telegram-бота
 * @param {string} title - Название тренировки
 * @param {string} description - Описание тренировки
 * @param {string} duration - Продолжительность
 * @param {string} intensity - Интенсивность
 * @returns {string} - HTML разметка для карточки
 */
function createWorkoutCard(title, description, duration, intensity) {
  return `
<b>${title}</b>
${description}

⏱️ <i>${duration}</i> | 🔥 <i>${intensity}</i>

<a href="workout_details">Подробнее</a> | <a href="start_workout">Начать</a>
  `.trim();
}

/**
 * Создает прогресс-бар для Telegram-бота
 * @param {number} value - Текущее значение (0-100)
 * @param {number} total - Максимальное значение
 * @param {string} color - Цвет прогресс-бара (из COLORS)
 * @returns {string} - Текстовое представление прогресс-бара
 */
function createProgressBar(value, total, color = COLORS.primary) {
  const percentage = Math.round((value / total) * 100);
  const filledBlocks = Math.round(percentage / 10);
  const emptyBlocks = 10 - filledBlocks;
  
  const filled = '█'.repeat(filledBlocks);
  const empty = '░'.repeat(emptyBlocks);
  
  return `${filled}${empty} ${percentage}% (${value}/${total})`;
}

/**
 * Создает статистическую карточку для Telegram-бота
 * @param {string} title - Заголовок статистики
 * @param {string} value - Значение
 * @param {string} icon - Иконка (эмодзи)
 * @returns {string} - Форматированный текст для статистики
 */
function createStatCard(title, value, icon) {
  return `${icon} <b>${title}</b>: ${value}`;
}

/**
 * Создает меню навигации для Telegram-бота
 * @param {string} activeSection - Активный раздел
 * @returns {Array} - Массив кнопок для клавиатуры
 */
function createNavigationMenu(activeSection) {
  const sections = [
    { name: 'Главная', icon: '🏠', callback: 'home' },
    { name: 'Тренировки', icon: '💪', callback: 'workouts' },
    { name: 'Статистика', icon: '📊', callback: 'statistics' },
    { name: 'Профиль', icon: '👤', callback: 'profile' }
  ];
  
  return sections.map(section => {
    const isActive = section.name === activeSection;
    const text = isActive ? `✅ ${section.icon} ${section.name}` : `${section.icon} ${section.name}`;
    return createButton(text, isActive ? COLORS.primary : COLORS.secondary, section.callback);
  });
}

// Экспорт функций для использования в основном коде бота
module.exports = {
  COLORS,
  createButton,
  createWorkoutCard,
  createProgressBar,
  createStatCard,
  createNavigationMenu
};
