// Загрузка заявок при открытии страницы
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('dashboard.html')) {
        loadRequests();
        loadClients(); // Загрузка клиентов для формы создания
    }
});

// Загрузка списка заявок
async function loadRequests() {
    try {
        // Получение фильтров
        const status = document.getElementById('filterStatus')?.value || '';

        // Формирование URL с параметрами
        let url = '/requests/?page=1&limit=100';
        if (status) url += `&status=${encodeURIComponent(status)}`;

        const response = await api.get(url);
        const data = await response.json();

        if (response.ok) {
            displayRequests(data.data || []);
            updateStatistics(data.data || []);
        } else {
            showAlert('Ошибка загрузки заявок: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('Error loading requests:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Отображение заявок в виде карточек
function displayRequests(requests) {
    const container = document.getElementById('requestsContainer');

    if (requests.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    Заявки не найдены
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = requests.map(request => `
        <div class="col-xl-4 col-lg-6 col-md-6">
            <div class="request-card ${getStatusClass(request.request_status)}">
                <!-- Заголовок карточки -->
                <div class="request-card-header">
                    <div class="request-id">
                        <i class="fas fa-hashtag"></i> ${request.request_id}
                    </div>
                    ${getStatusBadge(request.request_status)}
                </div>

                <!-- Тело карточки -->
                <div class="request-card-body">
                    <!-- Информация о технике -->
                    <div class="tech-info">
                        <div class="tech-icon">
                            <i class="fas fa-tools"></i>
                        </div>
                        <div class="tech-details">
                            <h5 class="tech-type">${request.tech_type}</h5>
                            <p class="tech-model">${request.tech_model}</p>
                        </div>
                    </div>

                    <!-- Мета информация -->
                    <div class="request-meta">
                        <div class="meta-item">
                            <i class="fas fa-calendar-alt"></i>
                            <span>Создана: ${formatDate(request.start_date)}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-user-cog"></i>
                            <span>${request.master_name || '<span class="text-danger">Не назначен</span>'}</span>
                        </div>
                        ${request.completion_date ? `
                            <div class="meta-item">
                                <i class="fas fa-check-circle text-success"></i>
                                <span>Завершена: ${formatDate(request.completion_date)}</span>
                            </div>
                        ` : ''}
                    </div>

                    <!-- Кнопка действия -->
                    <button class="btn btn-primary w-100" onclick="viewRequest(${request.request_id})">
                        <i class="fas fa-eye me-2"></i>Подробнее
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Получение класса для статуса
function getStatusClass(status) {
    const classes = {
        'Новая заявка': 'status-new',
        'В процессе ремонта': 'status-progress',
        'Готова к выдаче': 'status-ready',
        'Ожидание запчастей': 'status-waiting',
        'Завершена': 'status-completed'
    };
    return classes[status] || '';
}

// Получение бейджа статуса
function getStatusBadge(status) {
    const badges = {
        'Новая заявка': '<span class="badge bg-info"><i class="fas fa-star"></i> Новая</span>',
        'В процессе ремонта': '<span class="badge bg-warning"><i class="fas fa-tools"></i> В работе</span>',
        'Готова к выдаче': '<span class="badge bg-success"><i class="fas fa-check"></i> Готова</span>',
        'Ожидание запчастей': '<span class="badge bg-secondary"><i class="fas fa-clock"></i> Ожидание</span>',
        'Завершена': '<span class="badge bg-dark"><i class="fas fa-check-double"></i> Завершена</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
}

// Форматирование даты
function formatDate(dateString) {
    if (!dateString) return 'Не указана';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Обновление статистики
function updateStatistics(requests) {
    const total = requests.length;
    const newRequests = requests.filter(r => r.request_status === 'Новая заявка').length;
    const inProgress = requests.filter(r => r.request_status === 'В процессе ремонта').length;
    const completed = requests.filter(r =>
        r.request_status === 'Готова к выдаче' || r.request_status === 'Завершена'
    ).length;

    document.getElementById('statTotal').textContent = total;
    document.getElementById('statNew').textContent = newRequests;
    document.getElementById('statInProgress').textContent = inProgress;
    document.getElementById('statCompleted').textContent = completed;
}

// Загрузка списка клиентов для формы
async function loadClients() {
    try {
        const response = await api.get('/users/');
        const data = await response.json();

        if (response.ok) {
            const clients = (data.data || []).filter(user => user.user_type === 'Заказчик');
            const select = document.getElementById('client_id');

            if (select) {
                select.innerHTML = '<option value="">Выберите клиента</option>' +
                    clients.map(client =>
                        `<option value="${client.user_id}">${client.full_name}</option>`
                    ).join('');
            }
        }
    } catch (error) {
        console.error('Error loading clients:', error);
    }
}

// Создание новой заявки
async function handleCreateRequest(event) {
    event.preventDefault();

    const requestData = {
        tech_type: document.getElementById('tech_type').value,
        tech_model: document.getElementById('tech_model').value,
        problem_description: document.getElementById('problem_description').value,
        client_id: parseInt(document.getElementById('client_id').value)
    };

    try {
        const response = await api.post('/requests/', requestData);
        const data = await response.json();

        if (response.ok) {
            showAlert('Заявка успешно создана!', 'success');

            // Закрыть модальное окно
            const modal = bootstrap.Modal.getInstance(document.getElementById('createRequestModal'));
            modal.hide();

            // Очистить форму
            document.getElementById('createRequestForm').reset();

            // Обновить список заявок
            loadRequests();
        } else {
            showAlert('Ошибка создания заявки: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('Error creating request:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Глобальная переменная для хранения текущей заявки
let currentRequest = null;

// Просмотр деталей заявки (обновленная версия)
async function viewRequest(requestId) {
    try {
        const response = await api.get(`/requests/${requestId}`);
        const data = await response.json();

        if (response.ok) {
            currentRequest = data.data || data;

            // ✅ ИСПРАВЛЕНИЕ: Заполняем скрытое поле request_id для формы комментария
            const commentRequestIdField = document.getElementById('commentRequestId');
            if (commentRequestIdField) {
                commentRequestIdField.value = requestId;
            }

            // Заполнение модального окна просмотра
            document.getElementById('viewRequestId').textContent = currentRequest.request_id;
            document.getElementById('viewStatus').innerHTML = getStatusBadge(currentRequest.request_status);
            document.getElementById('viewTechType').textContent = currentRequest.tech_type || 'Не указан';
            document.getElementById('viewTechModel').textContent = currentRequest.tech_model || 'Не указана';
            document.getElementById('viewProblem').textContent = currentRequest.problem_description || 'Не указано';
            document.getElementById('viewMaster').textContent = currentRequest.master_name || 'Не назначен';
            document.getElementById('viewClient').textContent = currentRequest.client_name || 'Не указан';
            document.getElementById('viewStartDate').textContent = formatDate(currentRequest.start_date);
            document.getElementById('viewEndDate').textContent = formatDate(currentRequest.completion_date) || 'В работе';

            // Показать кнопки редактирования (только для Менеджера/Мастера)
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            if (user.user_type === 'Менеджер' || user.user_type === 'Мастер') {
                document.getElementById('editButtons').style.display = 'block';
            }

            // Загрузка комментариев
            loadRequestComments(requestId);

            // Загрузка QR-кода
            document.getElementById('qrFeedback').src = `${API_URL.replace('/api', '')}/qr/feedback`;

            // Открытие модального окна
            const modal = new bootstrap.Modal(document.getElementById('viewRequestModal'));
            modal.show();
        } else {
            showAlert('Ошибка загрузки заявки', 'danger');
        }
    } catch (error) {
        console.error('Error viewing request:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Открыть режим редактирования
async function openEditMode() {
    if (!currentRequest) return;

    // Заполнить форму текущими данными
    document.getElementById('editRequestId').textContent = currentRequest.request_id;
    document.getElementById('editStatus').value = currentRequest.request_status;
    document.getElementById('editTechType').value = currentRequest.tech_type || '';
    document.getElementById('editTechModel').value = currentRequest.tech_model || '';
    document.getElementById('editProblem').value = currentRequest.problem_description || '';

    // Загрузить список мастеров
    await loadMastersForEdit();

    // Установить текущего мастера
    document.getElementById('editMaster').value = currentRequest.master_id || '';

    // Закрыть окно просмотра и открыть окно редактирования
    bootstrap.Modal.getInstance(document.getElementById('viewRequestModal')).hide();
    const editModal = new bootstrap.Modal(document.getElementById('editRequestModal'));
    editModal.show();
}

// Загрузка мастеров для редактирования
async function loadMastersForEdit() {
    try {
        const response = await api.get('/users/specialists');
        const data = await response.json();

        if (response.ok) {
            const select = document.getElementById('editMaster');
            select.innerHTML = '<option value="">Не назначен</option>' +
                (data.data || []).map(master =>
                    `<option value="${master.user_id}">${master.full_name}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading masters:', error);
    }
}

// Сохранить изменения заявки
async function handleEditRequest(event) {
    event.preventDefault();

    if (!currentRequest) return;

    const updateData = {
        request_status: document.getElementById('editStatus').value,
        master_id: document.getElementById('editMaster').value || null,
        problem_description: document.getElementById('editProblem').value
    };

    try {
        const response = await api.put(`/requests/${currentRequest.request_id}`, updateData);
        const data = await response.json();

        if (response.ok) {
            showAlert('Заявка успешно обновлена!', 'success');

            bootstrap.Modal.getInstance(document.getElementById('editRequestModal')).hide();
            loadRequests();
            currentRequest = null;
        } else {
            showAlert('Ошибка обновления: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('Error updating request:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Быстрое назначение мастера
async function assignMaster() {
    // ✅ ИСПРАВЛЕНИЕ: Добавлена проверка request_id
    if (!currentRequest || !currentRequest.request_id) {
        showAlert('Ошибка: заявка не выбрана', 'danger');
        return;
    }

    await loadMastersForEdit();

    const masterId = prompt('Введите ID мастера:\n(Оставьте пустым для снятия назначения)');

    if (masterId === null) return;

    try {
        const response = await api.put(`/requests/${currentRequest.request_id}`, {
            master_id: masterId ? parseInt(masterId) : null
        });

        if (response.ok) {
            showAlert('Мастер назначен!', 'success');
            viewRequest(currentRequest.request_id);
            loadRequests();
        } else {
            const data = await response.json();
            showAlert('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        showAlert('Ошибка соединения', 'danger');
    }
}

// Быстрое изменение статуса
async function changeStatus() {
    if (!currentRequest) return;

    const statuses = ['Новая заявка', 'В процессе ремонта', 'Ожидание запчастей', 'Готова к выдаче', 'Завершена'];
    const newStatus = prompt(`Выберите новый статус:\n${statuses.map((s, i) => `${i+1}. ${s}`).join('\n')}\n\nВведите номер:`);

    if (!newStatus) return;

    const selectedStatus = statuses[parseInt(newStatus) - 1];
    if (!selectedStatus) {
        showAlert('Неверный номер статуса', 'danger');
        return;
    }

    try {
        const response = await api.put(`/requests/${currentRequest.request_id}`, {
            request_status: selectedStatus
        });

        if (response.ok) {
            showAlert('Статус изменен!', 'success');
            viewRequest(currentRequest.request_id);
            loadRequests();
        } else {
            const data = await response.json();
            showAlert('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        showAlert('Ошибка соединения', 'danger');
    }
}

// Добавить комментарий к заявке
function openAddComment(requestId) {
    document.getElementById('commentRequestId').textContent = requestId;
    currentRequest = { request_id: requestId };

    const modal = new bootstrap.Modal(document.getElementById('addCommentModal'));
    modal.show();
}

// Обработка добавления комментария (ПОЛНОСТЬЮ ПЕРЕПИСАНА)
async function handleAddComment(event) {
    event.preventDefault();

    const user = JSON.parse(localStorage.getItem('user') || '{}');

    // ✅ ИСПРАВЛЕНИЕ: Получаем request_id из скрытого поля
    const requestIdInput = document.getElementById('commentRequestId');
    const requestId = requestIdInput ? requestIdInput.value : null;

    if (!requestId) {
        showAlert('Ошибка: ID заявки не найден', 'danger');
        console.error('❌ commentRequestId field not found or empty');
        return;
    }

    const commentData = {
        message: document.getElementById('commentMessage').value,
        master_id: user.user_id,
        request_id: parseInt(requestId)  // ✅ Преобразуем в число
    };

    console.log('📤 Отправка комментария:', commentData);

    try {
        const response = await api.post('/comments/', commentData);
        const data = await response.json();

        if (response.ok) {
            showAlert('Комментарий добавлен!', 'success');

            // Закрыть окно и очистить форму
            bootstrap.Modal.getInstance(document.getElementById('addCommentModal')).hide();
            document.getElementById('addCommentForm').reset();

            // Обновить комментарии
            loadRequestComments(requestId);
        } else {
            showAlert('Ошибка добавления комментария: ' + (data.error || 'Неизвестная ошибка'), 'danger');
        }
    } catch (error) {
        console.error('❌ Error adding comment:', error);
        showAlert('Ошибка соединения с сервером', 'danger');
    }
}

// Загрузка комментариев к заявке
async function loadRequestComments(requestId) {
    try {
        const response = await api.get(`/comments/?request_id=${requestId}`);
        const data = await response.json();

        const commentsDiv = document.getElementById('viewComments');

        if (response.ok && data.data && data.data.length > 0) {
            commentsDiv.innerHTML = data.data.map(comment => `
                <div class="card mb-2">
                    <div class="card-body">
                        <h6 class="card-subtitle mb-2 text-muted">
                            ${comment.master_name || 'Мастер #' + comment.master_id}
                            <small class="text-muted">• ${formatDate(comment.created_at)}</small>
                        </h6>
                        <p class="card-text">${comment.message}</p>
                    </div>
                </div>
            `).join('');
        } else {
            commentsDiv.innerHTML = '<p class="text-muted"><i>Комментариев пока нет</i></p>';
        }
    } catch (error) {
        console.error('Error loading comments:', error);
        document.getElementById('viewComments').innerHTML =
            '<p class="text-danger">Ошибка загрузки комментариев</p>';
    }
}

// Сброс фильтров
function clearFilters() {
    document.getElementById('filterStatus').value = '';
    loadRequests();
}
