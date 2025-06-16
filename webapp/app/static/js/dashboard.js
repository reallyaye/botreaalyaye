document.addEventListener('DOMContentLoaded', function() {
  const csrfToken = document.querySelector('input[name="csrf_token"]').value;
  const upcomingWorkoutsList = document.getElementById('upcoming-workouts-list');
  const editScheduleModal = document.getElementById('edit-schedule-modal');
  const closeEditModalBtn = document.getElementById('close-edit-modal');
  const editScheduleForm = document.getElementById('edit-schedule-form');
  const editScheduleIdInput = document.getElementById('edit-schedule-id');
  const editActivityInput = document.getElementById('edit-activity');
  const editScheduledTimeInput = document.getElementById('edit-scheduled-time');

  // Function to refresh upcoming workouts list
  async function refreshUpcomingWorkouts() {
    try {
      const response = await fetch('/dashboard/upcoming-workouts');
      const html = await response.text();
      if (upcomingWorkoutsList) {
        upcomingWorkoutsList.innerHTML = html;
      }
      attachEventListenersToWorkoutButtons(); // Re-attach listeners after refresh
    } catch (error) {
      console.error('Error refreshing upcoming workouts:', error);
    }
  }

  // Function to attach event listeners to dynamic buttons
  function attachEventListenersToWorkoutButtons() {
    // Start button
    document.querySelectorAll('.start-schedule-btn').forEach(button => {
      button.removeEventListener('click', handleStartSchedule); // Prevent duplicate listeners
      button.addEventListener('click', handleStartSchedule);
    });

    // Edit button
    document.querySelectorAll('.edit-schedule-btn').forEach(button => {
      button.removeEventListener('click', handleEditSchedule);
      button.addEventListener('click', handleEditSchedule);
    });

    // Delete button
    document.querySelectorAll('.delete-schedule-btn').forEach(button => {
      button.removeEventListener('click', handleDeleteSchedule);
      button.addEventListener('click', handleDeleteSchedule);
    });
  }

  // Handlers for buttons
  async function handleStartSchedule(event) {
    const scheduleId = this.dataset.id;
    try {
      const response = await fetch(`/dashboard/start-schedule/${scheduleId}`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken // Assuming CSRF token is passed as a header for AJAX POST
        },
        body: new URLSearchParams({'csrf_token': csrfToken})
      });
      const result = await response.json();
      if (result.status === 'success') {
        alert(result.message);
        refreshUpcomingWorkouts();
        refreshDashboardStats(); // Call to refresh dashboard stats
      } else {
        alert('Ошибка: ' + result.message);
      }
    } catch (error) {
      console.error('Error starting schedule:', error);
      alert('Произошла ошибка сети или сервера.');
    }
  }

  async function handleEditSchedule(event) {
    const scheduleId = this.dataset.id;
    try {
      const response = await fetch(`/dashboard/schedule-data/${scheduleId}`);
      const data = await response.json();

      if (response.ok) {
        editScheduleIdInput.value = data.id;
        editActivityInput.value = data.activity;
        editScheduledTimeInput.value = data.scheduled_time;
        editScheduleModal.style.display = 'flex';
      } else {
        alert('Ошибка загрузки данных: ' + data.error);
      }
    } catch (error) {
      console.error('Error fetching schedule data:', error);
      alert('Произошла ошибка при загрузке данных тренировки.');
    }
  }

  async function handleDeleteSchedule(event) {
    const scheduleId = this.dataset.id;
    if (!confirm('Вы уверены, что хотите удалить эту тренировку?')) {
      return;
    }
    try {
      const response = await fetch(`/dashboard/delete-schedule/${scheduleId}`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken
        },
        body: new URLSearchParams({'csrf_token': csrfToken})
      });
      const result = await response.json();
      if (result.success) {
        alert('Тренировка успешно удалена!');
        refreshUpcomingWorkouts();
      } else {
        alert('Ошибка при удалении: ' + result.message);
      }
    } catch (error) {
      console.error('Error deleting schedule:', error);
      alert('Произошла ошибка сети или сервера.');
    }
  }

  // Modal close event
  if (closeEditModalBtn) {
    closeEditModalBtn.addEventListener('click', function() {
      editScheduleModal.style.display = 'none';
    });
  }

  // Edit form submission
  if (editScheduleForm) {
    editScheduleForm.addEventListener('submit', async function(event) {
      event.preventDefault();
      const scheduleId = editScheduleIdInput.value;
      const formData = new FormData(this);

      try {
        const response = await fetch(`/dashboard/edit-schedule/${scheduleId}`, {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json(); // Parse the response as JSON

        if (result.status === 'success') {
          alert(result.message);
          if (result.redirect_url) {
            window.location.href = result.redirect_url; // Redirect if success and URL is provided
          } else {
            refreshUpcomingWorkouts(); // Otherwise, just refresh the list
            refreshDashboardStats();
          }
        } else {
          alert('Ошибка: ' + result.message); // Display error message from backend
        }

      } catch (error) {
        console.error('Error updating schedule:', error);
        alert('Произошла ошибка при обновлении тренировки.');
      }
      editScheduleModal.style.display = 'none';
    });
  }

  // Function to refresh dashboard statistics
  async function refreshDashboardStats() {
    try {
      const response = await fetch('/dashboard/stats-json');
      const data = await response.json();
      if (response.ok) {
        document.getElementById('total-workouts').innerText = data.total_workouts;
        document.getElementById('total-minutes').innerText = data.total_minutes;
        document.getElementById('total-calories').innerText = data.total_calories;
        document.getElementById('achievements-count').innerText = data.achievements_count;
      } else {
        console.error('Error refreshing dashboard stats:', data.error);
      }
    } catch (error) {
      console.error('Network error refreshing dashboard stats:', error);
    }
  }

  // Initial call to attach event listeners when the page loads
  attachEventListenersToWorkoutButtons();
}); 