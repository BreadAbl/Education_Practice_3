// Загрузка пользователей при открытии страницы
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('users.html')) {
        checkManagerAccess(); // Проверка прав доступа
        loadUsers();
    }
});

// Проверка прав доступа (только менеджер)
function checkManagerAccess() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (user.user_type !== 'Менеджер') {
        showAlert('У вас нет прав для просмотра этой страницы', 'danger');
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 2000);
    }
}

// Загрузка списка пользователей
async function loadUsers() {
    try {
        const userType = document.getElementById('filterUserType')?.value || '';

        const response = await api.get('/users/');
        const data = await response.json();

        if (response.ok) {
            let users = data.data || [];

            // Фильтрация по роли
            if (userType) {
                users = users.filter(user => user.user_type === userType);
            }

            displayUsers(users);
        } else {
            showAlert('Ошибка загрузки пользователей: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Отображение пользователей в таблице
function displayUsers(users) {
    const tableBody = document.getElementById('usersTable');

    if (users.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    <i>Пользователи не найдены</i>
                </td>
            </tr>
        `;
        return;
    }

    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

    tableBody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.user_id}</strong></td>
            <td>${user.full_name}</td>
            <td><code>${user.login}</code></td>
            <td>${user.phone}</td>
            <td>${getRoleBadge(user.user_type)}</td>
            <td>
                ${user.user_id === currentUser.user_id
                    ? '<span class="text-muted">Вы</span>'
                    : `<button class="btn btn-sm btn-outline-danger" onclick="deleteUser(${user.user_id}, '${user.full_name}')">
                           Удалить
                       </button>`
                }
            </td>
        </tr>
    `).join('');
}

// Создание нового пользователя
async function handleCreateUser(event) {
    event.preventDefault();

    const userData = {
        full_name: document.getElementById('full_name').value,
        phone: document.getElementById('phone').value,
        login: document.getElementById('login').value,
        password: document.getElementById('password').value,
        user_type: document.getElementById('user_type').value
    };

    try {
        const response = await api.post('/users/', userData);
        const data = await response.json();

        if (response.ok) {
            showAlert('Пользователь успешно создан!', 'success');

            // Закрыть модальное окно
            const modal = bootstrap.Modal.getInstance(document.getElementById('createUserModal'));
            modal.hide();

            // Очистить форму
            document.getElementById('createUserForm').reset();

            // Обновить список пользователей
            loadUsers();
        } else {
            showAlert('Ошибка создания пользователя: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('Error creating user:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Удаление пользователя
async function deleteUser(userId, userName) {
    if (!confirm(`Вы уверены, что хотите удалить пользователя "${userName}"?`)) {
        return;
    }

    try {
        const response = await api.delete(`/users/${userId}`);
        const data = await response.json();

        if (response.ok) {
            showAlert('Пользователь успешно удален', 'success');
            loadUsers();
        } else {
            showAlert('Ошибка удаления: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}
