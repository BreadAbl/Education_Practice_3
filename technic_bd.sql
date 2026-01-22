-- ============================================================================
-- СИСТЕМА УПРАВЛЕНИЯ ЗАЯВКАМИ "БЫТСЕРВИС"
-- Только ремонт бытовой техники
-- ============================================================================

-- ============================================================================
-- 1. УДАЛЕНИЕ СТАРЫХ ТАБЛИЦ
-- ============================================================================

DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS repair_requests CASCADE;
DROP TABLE IF EXISTS requests CASCADE; -- На случай, если создавали с таким именем
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS user_type_enum CASCADE;
DROP TYPE IF EXISTS request_status_enum CASCADE;

-- ============================================================================
-- 2. СОЗДАНИЕ ТАБЛИЦ
-- ============================================================================

-- Таблица пользователей
CREATE TABLE users (
    user_id    SERIAL PRIMARY KEY,
    full_name  VARCHAR(100) NOT NULL,
    phone      VARCHAR(20)  NOT NULL,
    login      VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    user_type  VARCHAR(50)  NOT NULL CHECK (user_type IN (
        'Менеджер',
        'Мастер',
        'Оператор',
        'Заказчик',
        'Менеджер по качеству'
    ))
);

-- Таблица заявок (repair_requests - чтобы сервер не падал)
CREATE TABLE repair_requests (
    request_id           SERIAL PRIMARY KEY,
    start_date           DATE        NOT NULL,
    tech_type            VARCHAR(100) NOT NULL,  -- Фен, Холодильник и т.п.
    tech_model           VARCHAR(150) NOT NULL,
    problem_description  TEXT        NOT NULL,
    request_status       VARCHAR(50) NOT NULL DEFAULT 'Новая заявка' CHECK (request_status IN (
        'Новая заявка',
        'В процессе ремонта',
        'Готова к выдаче',
        'Ожидание запчастей',
        'Завершена',
        'Выполнена',            -- Добавил для совместимости
        'Ожидание комплектующих' -- Добавил для совместимости
    )),
    completion_date      DATE,
    repair_parts         VARCHAR(255),
    master_id            INT,
    client_id            INT NOT NULL,

    CONSTRAINT fk_requests_master
        FOREIGN KEY (master_id) REFERENCES users(user_id),
    CONSTRAINT fk_requests_client
        FOREIGN KEY (client_id) REFERENCES users(user_id),
    CONSTRAINT check_completion_date
        CHECK (completion_date IS NULL OR completion_date >= start_date)
);

-- Таблица комментариев
CREATE TABLE comments (
    comment_id  SERIAL PRIMARY KEY,
    message     TEXT NOT NULL,
    master_id   INT,
    request_id  INT  NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_comments_master
        FOREIGN KEY (master_id) REFERENCES users(user_id),
    CONSTRAINT fk_comments_request
        FOREIGN KEY (request_id) REFERENCES repair_requests(request_id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. СОЗДАНИЕ ИНДЕКСОВ
-- ============================================================================

CREATE INDEX idx_users_type          ON users(user_type);
CREATE INDEX idx_requests_status     ON repair_requests(request_status);
CREATE INDEX idx_requests_master     ON repair_requests(master_id);
CREATE INDEX idx_requests_client     ON repair_requests(client_id);
CREATE INDEX idx_comments_request    ON comments(request_id);

-- ============================================================================
-- 4. ЗАПОЛНЕНИЕ ДАННЫХ (ТОЛЬКО БЫТСЕРВИС)
-- ============================================================================

-- ПОЛЬЗОВАТЕЛИ - inputDataUsers.xlsx #5
INSERT INTO users (full_name, phone, login, password, user_type) VALUES
('Трубин Никита Юрьевич',           '89210563128', 'kasoo',              'root',                'Менеджер'),
('Мурашов Андрей Юрьевич',          '89535078985', 'murashov123',        'qwerty',              'Мастер'),
('Степанов Андрей Викторович',      '89210673849', 'test1',              'test1',               'Мастер'),
('Перина Анастасия Денисовна',      '89990563748', 'perinaAD',           '250519',              'Оператор'),
('Мажитова Ксения Сергеевна',       '89994563847', 'krutiha1234567',     '1234567890',          'Оператор'),
('Семенова Ясмина Марковна',        '89994563847', 'login1',             'pass1',               'Мастер'),
('Баранова Эмилия Марковна',        '89994563841', 'login2',             'pass2',               'Заказчик'),
('Егорова Алиса Платоновна',        '89994563842', 'login3',             'pass3',               'Заказчик'),
('Титов Максим Иванович',           '89994563843', 'login4',             'pass4',               'Заказчик'),
('Иванов Марк Максимович',          '89994563844', 'login5',             'pass5',               'Мастер');

-- ЗАЯВКИ - inputDataRequests.xlsx #1
INSERT INTO repair_requests (start_date, tech_type, tech_model, problem_description, request_status, completion_date, repair_parts, master_id, client_id)
VALUES
('2023-06-06', 'Фен', 'Ладомир ТА112 белый', 'Перестал работать', 'В процессе ремонта', NULL, NULL, 2, 7),
('2023-05-05', 'Тостер', 'Redmond RT-437 черный', 'Перестал работать', 'В процессе ремонта', NULL, NULL, 3, 7),
('2022-07-07', 'Холодильник', 'Indesit DS 316 W белый', 'Не морозит одна из камер холодильника', 'Готова к выдаче', '2023-01-01', NULL, 2, 8),
('2023-08-02', 'Стиральная машина', 'DEXP WM-F610NTMA/WW белый', 'Перестали работать многие режимы стирки', 'Новая заявка', NULL, NULL, NULL, 8),
('2023-08-02', 'Мультиварка', 'Redmond RMC-M95 черный', 'Перестала включаться', 'Новая заявка', NULL, NULL, NULL, 9),
('2023-08-02', 'Фен', 'Ладомир ТА113 чёрный', 'Перестал работать', 'Готова к выдаче', '2023-08-03', NULL, 2, 7),
('2023-07-09', 'Холодильник', 'Indesit DS 314 W серый', 'Гудит, но не замораживает', 'Готова к выдаче', '2023-08-03', 'Мотор обдува морозильной камеры холодильника', 2, 8);

-- КОММЕНТАРИИ - inputDataComments.xlsx #3
INSERT INTO comments (message, master_id, request_id) VALUES
('Интересная поломка', 2, 1),
('Очень странно, будем разбираться!', 3, 2),
('Скорее всего потребуется мотор обдува!', 2, 7),
('Интересная поломка', 2, 1),
('Очень странно, будем разбираться!', 3, 6);

-- ============================================================================
-- 5. СОЗДАНИЕ ПРЕДСТАВЛЕНИЙ (VIEWS) ДЛЯ СОВМЕСТИМОСТИ
-- Чтобы код, который ищет таблицу 'requests' или 'masters', тоже работал
-- ============================================================================

-- Представление REQUESTS (для нового кода)
CREATE OR REPLACE VIEW requests AS
SELECT
    request_id,
    start_date,
    tech_type as home_tech_type,
    tech_model as home_tech_model,
    problem_description,
    request_status,
    completion_date,
    master_id,
    client_id
FROM repair_requests;

-- Представление MASTERS (выбирает только мастеров из users)
CREATE OR REPLACE VIEW masters AS
SELECT
    user_id as master_id,
    full_name,
    'Общий профиль' as specialization,
    phone,
    true as is_active,
    user_id
FROM users
WHERE user_type = 'Мастер';

-- Представление CLIENTS (выбирает только заказчиков из users)
CREATE OR REPLACE VIEW clients AS
SELECT
    user_id as client_id,
    full_name,
    phone,
    '' as email,
    '' as address
FROM users
WHERE user_type = 'Заказчик';
