// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop();
    const isLoginPage = currentPage === 'index.html' || currentPage === '';
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // Если не на странице входа и нет токена - редирект на вход
    if (!isLoginPage && !token) {
        window.location.href = 'index.html';
        return;
    }

    // Если на странице входа и есть токен - редирект на дашборд
    if (isLoginPage && token) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Отображение имени пользователя
    const userNameElement = document.getElementById('userName');
    if (userNameElement && user.full_name) {
        userNameElement.textContent = user.full_name;
    }

    // Показать ссылку "Пользователи" только для менеджера
    const usersLink = document.getElementById('usersLink');
    if (usersLink && user.user_type === 'Менеджер') {
        usersLink.style.display = 'block';
    }
});

// Обработка входа
async function handleLogin(event) {
    event.preventDefault();

    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ login, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Сохранение токена и данных пользователя
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data));

            // Редирект на дашборд
            window.location.href = 'dashboard.html';
        } else {
            // Показать ошибку
            errorMessage.textContent = data.error || 'Ошибка входа';
            errorMessage.classList.remove('d-none');
        }
    } catch (error) {
        errorMessage.textContent = 'Ошибка соединения с сервером';
        errorMessage.classList.remove('d-none');
        console.error('Login error:', error);
    }
}

// Выход из системы
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}
