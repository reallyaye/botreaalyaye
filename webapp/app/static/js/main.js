/**
 * NOVIII Fitness Bot & WebApp - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  // Анимация появления элементов
  const fadeElements = document.querySelectorAll('.fade-in');
  fadeElements.forEach((element, index) => {
    setTimeout(() => {
      element.style.opacity = '1';
      element.style.transform = 'translateY(0)';
    }, 100 * index);
  });

  // Обработка фильтров
  const filterButtons = document.querySelectorAll('.chart-filter');
  filterButtons.forEach(button => {
    button.addEventListener('click', function() {
      const parent = this.parentElement;
      parent.querySelectorAll('.chart-filter').forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Обработка вкладок
  const tabs = document.querySelectorAll('.profile-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Мобильное меню
  const menuToggle = document.createElement('button');
  menuToggle.className = 'menu-toggle';
  menuToggle.innerHTML = '☰';
  menuToggle.style.display = 'none';
  menuToggle.style.background = 'none';
  menuToggle.style.border = 'none';
  menuToggle.style.fontSize = '24px';
  menuToggle.style.cursor = 'pointer';
  menuToggle.style.color = 'var(--primary)';
  
  const headerContainer = document.querySelector('.header-container');
  const navList = document.querySelector('.nav-list');
  
  if (headerContainer && navList) {
    headerContainer.insertBefore(menuToggle, headerContainer.firstChild);
    
    menuToggle.addEventListener('click', function() {
      navList.style.display = navList.style.display === 'flex' ? 'none' : 'flex';
    });
    
    // Адаптивное меню
    function handleResize() {
      if (window.innerWidth <= 768) {
        menuToggle.style.display = 'block';
        navList.style.display = 'none';
        navList.style.position = 'absolute';
        navList.style.top = '60px';
        navList.style.left = '0';
        navList.style.width = '100%';
        navList.style.flexDirection = 'column';
        navList.style.backgroundColor = 'var(--card-bg)';
        navList.style.boxShadow = 'var(--shadow-md)';
        navList.style.zIndex = '100';
        navList.style.padding = '10px 0';
      } else {
        menuToggle.style.display = 'none';
        navList.style.display = 'flex';
        navList.style.position = 'static';
        navList.style.flexDirection = 'row';
        navList.style.width = 'auto';
        navList.style.boxShadow = 'none';
        navList.style.padding = '0';
      }
    }
    
    window.addEventListener('resize', handleResize);
    handleResize();
  }

  // Инициализация графиков, если они есть на странице
  if (typeof Chart !== 'undefined') {
    // График активности
    const activityChart = document.getElementById('activityChart');
    if (activityChart) {
      const activityCtx = activityChart.getContext('2d');
      new Chart(activityCtx, {
        type: 'bar',
        data: {
          labels: ['1 мая', '5 мая', '10 мая', '15 мая', '20 мая', '25 мая', '30 мая'],
          datasets: [{
            label: 'Тренировки (мин)',
            data: [45, 60, 30, 90, 40, 75, 60],
            backgroundColor: 'rgba(67, 97, 238, 0.7)',
            borderColor: 'rgba(67, 97, 238, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }

    // График распределения тренировок
    const distributionChart = document.getElementById('distributionChart');
    if (distributionChart) {
      const distributionCtx = distributionChart.getContext('2d');
      new Chart(distributionCtx, {
        type: 'doughnut',
        data: {
          labels: ['Бег', 'Силовые', 'Йога', 'Плавание', 'HIIT'],
          datasets: [{
            data: [30, 25, 15, 20, 10],
            backgroundColor: [
              'rgba(67, 97, 238, 0.7)',
              'rgba(58, 12, 163, 0.7)',
              'rgba(76, 201, 240, 0.7)',
              'rgba(77, 204, 189, 0.7)',
              'rgba(247, 37, 133, 0.7)'
            ],
            borderColor: [
              'rgba(67, 97, 238, 1)',
              'rgba(58, 12, 163, 1)',
              'rgba(76, 201, 240, 1)',
              'rgba(77, 204, 189, 1)',
              'rgba(247, 37, 133, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
    }

    // График веса
    const weightChart = document.getElementById('weightChart');
    if (weightChart) {
      const weightCtx = weightChart.getContext('2d');
      new Chart(weightCtx, {
        type: 'line',
        data: {
          labels: ['1 мая', '5 мая', '10 мая', '15 мая', '20 мая', '25 мая'],
          datasets: [{
            label: 'Вес (кг)',
            data: [81, 80.5, 79.8, 79.2, 78.5, 78],
            backgroundColor: 'rgba(67, 97, 238, 0.1)',
            borderColor: 'rgba(67, 97, 238, 1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              min: 75,
              max: 82
            }
          }
        }
      });
    }
  }
});
