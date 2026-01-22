// Конфигурация API
const API_URL = 'http://192.168.0.21:5000/api';

// Утилиты для работы с API
const api = {
    // GET-запрос
    get: async (endpoint) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        // Проверка на истечение токена
        if (response.status === 401) {
            try {
                const data = await response.json();
                if (data.error && (data.error.includes('expired') || data.error.includes('Invalid token'))) {
                    showAlert('Сессия истекла. Войдите снова.', 'warning');
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        window.location.href = 'index.html';
                    }, 2000);
                }
            } catch (e) {}
        }

        return response;
    },

    // POST-запрос
    post: async (endpoint, data) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            try {
                const responseData = await response.json();
                if (responseData.error && (responseData.error.includes('expired') || responseData.error.includes('Invalid token'))) {
                    showAlert('Сессия истекла. Войдите снова.', 'warning');
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        window.location.href = 'index.html';
                    }, 2000);
                }
            } catch (e) {}
        }

        return response;
    },

    // PUT-запрос (для обновления)
    put: async (endpoint, data) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.status === 401) {
            try {
                const responseData = await response.json();
                if (responseData.error && (responseData.error.includes('expired') || responseData.error.includes('Invalid token'))) {
                    showAlert('Сессия истекла. Войдите снова.', 'warning');
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        window.location.href = 'index.html';
                    }, 2000);
                }
            } catch (e) {}
        }

        return response;
    },

    // DELETE-запрос
    delete: async (endpoint) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            try {
                const data = await response.json();
                if (data.error && (data.error.includes('expired') || data.error.includes('Invalid token'))) {
                    showAlert('Сессия истекла. Войдите снова.', 'warning');
                    setTimeout(() => {
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                        window.location.href = 'index.html';
                    }, 2000);
                }
            } catch (e) {}
        }

        return response;
    }
};

// Показать уведомление
function showAlert(message, type = 'danger') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Форматирование даты
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Получить бейдж статуса
function getStatusBadge(status) {
    const badges = {
        'Новая заявка': 'bg-info',
        'В процессе ремонта': 'bg-warning',
        'Готова к выдаче': 'bg-success',
        'Завершена': 'bg-secondary',
        'Ожидание запчастей': 'bg-danger'
    };
    const badgeClass = badges[status] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${status}</span>`;
}

// Получить бейдж роли
function getRoleBadge(role) {
    const badges = {
        'Менеджер': 'bg-danger',
        'Мастер': 'bg-primary',
        'Оператор': 'bg-info',
        'Заказчик': 'bg-secondary'
    };
    const badgeClass = badges[role] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${role}</span>`;
}
