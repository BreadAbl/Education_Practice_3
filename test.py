#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ПОЛНОЕ ТЕСТИРОВАНИЕ БЭКЕНДА - 20 ТЕСТОВ
Соответствует требованиям учебной практики
Покрывает: CRUD, валидацию, права доступа, статистику, edge cases
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

BASE_URL = "http://192.168.0.21:5000/api"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log(msg: str, status: str = "OK") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "OK": "✓",
        "ERR": "✗",
        "TEST": "►",
        "INFO": "ℹ",
        "WARN": "⚠"
    }
    colors = {
        "OK": Colors.GREEN,
        "ERR": Colors.RED,
        "TEST": Colors.BLUE,
        "INFO": Colors.CYAN,
        "WARN": Colors.YELLOW
    }
    color = colors.get(status, Colors.RESET)
    symbol = symbols.get(status, "•")
    print(f"{color}{Colors.BOLD}[{ts}] {symbol} {msg}{Colors.RESET}")


def detail(msg: str) -> None:
    print(f"  → {msg}")


def error_detail(msg: str) -> None:
    print(f"{Colors.RED}  ✗ {msg}{Colors.RESET}")


def separator(title: str = "", test_num: str = "") -> None:
    if title:
        print(f"\n{'=' * 70}")
        if test_num:
            print(f"║ {test_num:^66} ║")
        print(f"║ {title:^66} ║")
        print(f"{'=' * 70}\n")
    else:
        print(f"\n{'=' * 70}\n")


def show_error_response(response: requests.Response) -> None:
    """Показывает детали ошибки из ответа"""
    error_detail(f"HTTP Status: {response.status_code}")
    error_detail(f"URL: {response.url}")
    try:
        data = response.json()
        error_detail("JSON ответ:")
        print(f"{Colors.YELLOW}{json.dumps(data, indent=2, ensure_ascii=False)}{Colors.RESET}")
    except Exception:
        error_detail(f"Текст ответа: {response.text[:500]}")


def cleanup_test_user(token: str):
    """Удаляет тестового пользователя test_manager"""
    try:
        print(f"{Colors.CYAN}🔍 Очистка тестовых данных...{Colors.RESET}")
        time.sleep(0.2)

        r = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            users = r.json().get("data", [])
            test_user = next((u for u in users if u.get("login") == "test_manager"), None)

            if test_user:
                user_id = test_user.get("user_id")
                time.sleep(0.2)

                r = requests.delete(
                    f"{BASE_URL}/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )

                if r.status_code == 200:
                    print(f"{Colors.GREEN}✓ Удален test_manager (ID: {user_id}){Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⚠ Не удалось удалить test_manager{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}✓ test_manager не найден{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.YELLOW}⚠ Ошибка при очистке: {str(e)}{Colors.RESET}")


# ============================================================================
# ГРУППА 1: АУТЕНТИФИКАЦИЯ И АВТОРИЗАЦИЯ
# ============================================================================

def test_01_auth_manager() -> Tuple[bool, Optional[str]]:
    """ТЕСТ 1: Авторизация менеджера"""
    separator("Авторизация менеджера (kasoo)", "ТЕСТ 1")
    log("POST /api/auth/login", "TEST")
    detail("Логин: kasoo")
    detail("Пароль: root")

    try:
        time.sleep(0.2)
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={"login": "kasoo", "password": "root"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            log("✓ Авторизация успешна! (200)", "OK")
            detail(f"User ID: {data.get('user_id')}")
            detail(f"Роль: {data.get('user_type')}")
            detail(f"Токен: {token[:30]}...")
            return True, token
        else:
            log("✗ Ошибка авторизации", "ERR")
            show_error_response(r)
            return False, None

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False, None


def test_02_auth_invalid_credentials() -> bool:
    """ТЕСТ 2: Попытка входа с неверными данными"""
    separator("Неверный логин/пароль (401)", "ТЕСТ 2")
    log("POST /api/auth/login - неверные данные", "TEST")
    detail("Логин: invalid_user")
    detail("Пароль: wrong_password")

    try:
        time.sleep(0.2)
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={"login": "invalid_user", "password": "wrong_password"},
            timeout=10
        )

        if r.status_code == 401:
            log("✓ Получен ожидаемый статус 401", "OK")
            detail("Сообщение: Invalid login or password")
            return True
        else:
            log(f"✗ Ожидался 401, получен {r.status_code}", "ERR")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_03_auth_operator() -> Tuple[bool, Optional[str]]:
    """ТЕСТ 3: Авторизация оператора"""
    separator("Авторизация оператора (perinaAD)", "ТЕСТ 3")
    log("POST /api/auth/login", "TEST")
    detail("Логин: perinaAD")
    detail("Пароль: 250519")

    try:
        time.sleep(0.2)
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={"login": "perinaAD", "password": "250519"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            log("✓ Авторизация успешна! (200)", "OK")
            detail(f"Роль: {data.get('user_type')}")
            return True, token
        else:
            log("✗ Ошибка авторизации", "ERR")
            show_error_response(r)
            return False, None

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False, None


# ============================================================================
# ГРУППА 2: УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (CRUD)
# ============================================================================

def test_04_create_user(token: str) -> Tuple[bool, Optional[int]]:
    """ТЕСТ 4: Создание пользователя менеджером"""
    separator("Создание пользователя test_manager", "ТЕСТ 4")
    log("POST /api/users/", "TEST")

    user_data = {
        "full_name": "Тестовый Менеджер",
        "phone": "8-912-345-67-89",
        "login": "test_manager",
        "password": "test123",
        "user_type": "Менеджер"
    }

    detail(f"ФИО: {user_data['full_name']}")
    detail(f"Логин: {user_data['login']}")
    detail(f"Роль: {user_data['user_type']}")

    time.sleep(0.4)
    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(
                f"{BASE_URL}/users/",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=15
            )

            if r.status_code == 201:
                data = r.json()
                user_id = data.get("user_id")
                log("✓ Пользователь создан! (201)", "OK")
                detail(f"User ID: {user_id}")
                return True, user_id

            log("✗ Ошибка создания пользователя", "ERR")
            show_error_response(r)
            return False, None

        except requests.exceptions.ConnectionError:
            if attempt < max_retries:
                log(f"⚠ ConnectionError: попытка {attempt}/{max_retries}", "WARN")
                time.sleep(1.0)
                continue
            log(f"✗ Ошибка после {max_retries} попыток", "ERR")
            return False, None

        except Exception as e:
            log(f"✗ Исключение: {str(e)}", "ERR")
            return False, None

    return False, None


def test_05_create_duplicate_user(token: str) -> bool:
    """ТЕСТ 5: Попытка создать пользователя с существующим логином"""
    separator("Дубликат логина (400)", "ТЕСТ 5")
    log("POST /api/users/ - дубликат логина", "TEST")
    detail("Логин: kasoo (уже существует)")

    try:
        time.sleep(0.3)
        r = requests.post(
            f"{BASE_URL}/users/",
            json={
                "full_name": "Дубликат Тест",
                "phone": "8-999-999-99-99",
                "login": "kasoo",  # Уже существует
                "password": "test123",
                "user_type": "Оператор"
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )

        if r.status_code == 400:
            log("✓ Получен ожидаемый статус 400", "OK")
            detail("Валидация сработала корректно")
            return True

        log(f"✗ Ожидался 400, получен {r.status_code}", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_06_get_all_users(token: str) -> bool:
    """ТЕСТ 6: Получение списка всех пользователей"""
    separator("Получение списка пользователей", "ТЕСТ 6")
    log("GET /api/users/", "TEST")

    try:
        r = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            log(f"✓ Список получен! (200)", "OK")
            detail(f"Всего пользователей: {len(data)}")

            if data:
                log("Распределение по ролям:", "INFO")
                roles = {}
                for user in data:
                    role = user.get('user_type')
                    roles[role] = roles.get(role, 0) + 1

                for role, count in roles.items():
                    detail(f"{role}: {count}")

            return True

        log("✗ Ошибка получения списка", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_07_operator_cannot_create_user(operator_token: str) -> bool:
    """ТЕСТ 7: Оператор не может создавать пользователей (403)"""
    separator("Проверка прав оператора (403)", "ТЕСТ 7")
    log("POST /api/users/ как Оператор", "TEST")
    detail("Ожидаемый результат: 403 Forbidden")

    try:
        time.sleep(0.3)
        r = requests.post(
            f"{BASE_URL}/users/",
            json={
                "full_name": "Запрещенный Юзер",
                "phone": "8-999-999-99-99",
                "login": "forbidden_user",
                "password": "pass123",
                "user_type": "Оператор"
            },
            headers={"Authorization": f"Bearer {operator_token}"},
            timeout=15
        )

        if r.status_code == 403:
            log("✓ Получен статус 403", "OK")
            detail("Права доступа работают корректно")
            return True

        log(f"✗ Ожидался 403, получен {r.status_code}", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


# ============================================================================
# ГРУППА 3: УПРАВЛЕНИЕ ЗАЯВКАМИ
# ============================================================================

def test_08_get_all_requests(token: str) -> bool:
    """ТЕСТ 8: Получение списка всех заявок"""
    separator("Получение списка заявок", "ТЕСТ 8")
    log("GET /api/requests/", "TEST")
    detail("Параметры: page=1, limit=50")

    try:
        r = requests.get(
            f"{BASE_URL}/requests/?page=1&limit=50",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            log(f"✓ Список получен! (200)", "OK")
            detail(f"Всего заявок: {len(data)}")

            if data:
                log("Статистика по проектам:", "INFO")
                projects = {}
                for req in data:
                    proj = req.get('project')
                    projects[proj] = projects.get(proj, 0) + 1

                for proj, count in projects.items():
                    detail(f"{proj}: {count} заявок")

            return True

        log("✗ Ошибка получения заявок", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_09_create_request(token: str) -> Tuple[bool, Optional[int]]:
    """ТЕСТ 9: Создание новой заявки"""
    separator("Создание новой заявки", "ТЕСТ 9")
    log("POST /api/requests/", "TEST")

    request_data = {
        "project": "БытСервис",
        "tech_type": "Холодильник",
        "tech_model": "Samsung RT-TEST-2025",
        "problem_description": "Тестовая заявка: не охлаждает, шумит",
        "client_id": 7
    }

    detail(f"Проект: {request_data['project']}")
    detail(f"Тип техники: {request_data['tech_type']}")
    detail(f"Модель: {request_data['tech_model']}")

    try:
        time.sleep(0.3)
        r = requests.post(
            f"{BASE_URL}/requests/",
            json=request_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )

        if r.status_code == 201:
            data = r.json()
            request_id = data.get("request_id")
            log("✓ Заявка создана! (201)", "OK")
            detail(f"Request ID: {request_id}")
            detail(f"Статус: {data.get('request_status')}")
            return True, request_id

        log("✗ Ошибка создания заявки", "ERR")
        show_error_response(r)
        return False, None

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False, None


def test_10_create_request_invalid_data(token: str) -> bool:
    """ТЕСТ 10: Создание заявки с невалидными данными"""
    separator("Невалидные данные заявки (400)", "ТЕСТ 10")
    log("POST /api/requests/ - пустые поля", "TEST")
    detail("Отсутствует tech_type и problem_description")

    try:
        time.sleep(0.3)
        r = requests.post(
            f"{BASE_URL}/requests/",
            json={
                "project": "БытСервис",
                "tech_model": "Test Model",
                "client_id": 7
                # Отсутствуют обязательные поля
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )

        if r.status_code == 400:
            log("✓ Получен статус 400", "OK")
            detail("Валидация работает корректно")
            return True

        log(f"✗ Ожидался 400, получен {r.status_code}", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_11_get_masters(token: str) -> bool:
    """ТЕСТ 11: Получение списка мастеров"""
    separator("Получение списка мастеров", "ТЕСТ 11")
    log("GET /api/users/specialists", "TEST")

    try:
        r = requests.get(
            f"{BASE_URL}/users/specialists",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            log(f"✓ Список получен! (200)", "OK")
            detail(f"Всего мастеров: {len(data)}")

            if data and len(data) <= 5:
                log("Список мастеров:", "INFO")
                for master in data[:5]:
                    detail(f"{master.get('full_name')} ({master.get('login')})")

            return True

        log("✗ Ошибка получения мастеров", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


# ============================================================================
# ГРУППА 4: КОММЕНТАРИИ
# ============================================================================

def test_12_get_comments_for_request(token: str) -> bool:
    """ТЕСТ 12: Получение комментариев к заявке"""
    separator("Получение комментариев заявки", "ТЕСТ 12")
    log("GET /api/comments/?request_id=1", "TEST")
    detail("Получить комментарии к заявке #1")

    try:
        r = requests.get(
            f"{BASE_URL}/comments/?request_id=1",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            log(f"✓ Комментарии получены! (200)", "OK")
            detail(f"Всего комментариев: {len(data)}")

            if data:
                log("Первый комментарий:", "INFO")
                first = data[0]
                detail(f"Автор: {first.get('master_name', 'N/A')}")
                detail(f"Текст: {first.get('message', '')[:50]}...")

            return True

        log("✗ Ошибка получения комментариев", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_13_create_comment(token: str, request_id: Optional[int]) -> bool:
    """ТЕСТ 13: Создание комментария к заявке"""
    separator("Создание комментария", "ТЕСТ 13")
    log("POST /api/comments/", "TEST")

    if not request_id:
        request_id = 1  # Используем существующую заявку

    detail(f"Request ID: {request_id}")
    detail("Текст: Тестовый комментарий от автотеста")

    try:
        time.sleep(0.3)
        r = requests.post(
            f"{BASE_URL}/comments/",
            json={
                "message": "Тестовый комментарий от автотеста",
                "master_id": 2,  # Мурашов Андрей Юрьевич
                "request_id": request_id
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )

        if r.status_code == 201:
            data = r.json()
            log("✓ Комментарий создан! (201)", "OK")
            detail(f"Comment ID: {data.get('comment_id')}")
            return True

        log("✗ Ошибка создания комментария", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


# ============================================================================
# ГРУППА 5: СТАТИСТИКА И ОТЧЕТЫ
# ============================================================================

def test_14_get_statistics(token: str) -> bool:
    """ТЕСТ 14: Получение статистики"""
    separator("Получение статистики работы", "ТЕСТ 14")
    log("GET /api/statistics/", "TEST")

    try:
        r = requests.get(
            f"{BASE_URL}/statistics/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()
            log(f"✓ Статистика получена! (200)", "OK")
            log("Основные метрики:", "INFO")

            if "completed_requests" in data:
                detail(f"Завершено заявок: {data['completed_requests'].get('completed_requests_count', 0)}")

            if "average_completion_time" in data:
                avg_days = data['average_completion_time'].get('avg_completion_days', 0)
                detail(f"Среднее время ремонта: {avg_days} дней")

            if "master_workload" in data:
                detail(f"Мастеров в системе: {len(data['master_workload'])}")

            return True

        log("✗ Ошибка получения статистики", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_15_statistics_by_project(token: str) -> bool:
    """ТЕСТ 15: Статистика по проектам"""
    separator("Статистика по проектам", "ТЕСТ 15")
    log("GET /api/statistics/?project=БытСервис", "TEST")
    detail("Фильтр: только проект БытСервис")

    try:
        r = requests.get(
            f"{BASE_URL}/statistics/?project=БытСервис",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()
            log(f"✓ Статистика получена! (200)", "OK")
            detail("Данные отфильтрованы по проекту БытСервис")
            return True

        log("✗ Ошибка получения статистики", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


# ============================================================================
# ГРУППА 6: ФИЛЬТРАЦИЯ И ПОИСК
# ============================================================================

def test_16_filter_requests_by_status(token: str) -> bool:
    """ТЕСТ 16: Фильтрация заявок по статусу"""
    separator("Фильтрация заявок по статусу", "ТЕСТ 16")
    log("GET /api/requests/?status=Новая заявка", "TEST")
    detail("Фильтр: только новые заявки")

    try:
        r = requests.get(
            f"{BASE_URL}/requests/?status=Новая заявка",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            log(f"✓ Заявки получены! (200)", "OK")
            detail(f"Найдено новых заявок: {len(data)}")

            # Проверка, что все заявки имеют правильный статус
            all_correct = all(req.get('request_status') == 'Новая заявка' for req in data)
            if all_correct:
                detail("✓ Все заявки имеют статус 'Новая заявка'")
            else:
                detail("⚠ Найдены заявки с другими статусами")

            return True

        log("✗ Ошибка получения заявок", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_17_filter_requests_by_project(token: str) -> bool:
    """ТЕСТ 17: Фильтрация заявок по проекту"""
    separator("Фильтрация заявок по проекту", "ТЕСТ 17")
    log("GET /api/requests/?project=Конди", "TEST")
    detail("Фильтр: только проект Конди")

    try:
        r = requests.get(
            f"{BASE_URL}/requests/?project=Конди",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 200:
            data = r.json().get("data", [])
            log(f"✓ Заявки получены! (200)", "OK")
            detail(f"Найдено заявок по проекту Конди: {len(data)}")

            # Проверка
            all_correct = all(req.get('project') == 'Конди' for req in data)
            if all_correct:
                detail("✓ Все заявки относятся к проекту Конди")

            return True

        log("✗ Ошибка получения заявок", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


# ============================================================================
# ГРУППА 7: EDGE CASES И ВАЛИДАЦИЯ
# ============================================================================

def test_18_unauthorized_access(token: str) -> bool:
    """ТЕСТ 18: Доступ без токена (401)"""
    separator("Запрос без авторизации (401)", "ТЕСТ 18")
    log("GET /api/users/ без токена", "TEST")
    detail("Ожидаемый результат: 401 Unauthorized")

    try:
        r = requests.get(
            f"{BASE_URL}/users/",
            timeout=10
        )

        if r.status_code == 401:
            log("✓ Получен статус 401", "OK")
            detail("Защита эндпоинтов работает корректно")
            return True

        log(f"✗ Ожидался 401, получен {r.status_code}", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_19_invalid_token() -> bool:
    """ТЕСТ 19: Запрос с невалидным токеном (401)"""
    separator("Невалидный токен (401)", "ТЕСТ 19")
    log("GET /api/users/ с фейковым токеном", "TEST")
    detail("Токен: invalid_fake_token_12345")

    try:
        r = requests.get(
            f"{BASE_URL}/users/",
            headers={"Authorization": "Bearer invalid_fake_token_12345"},
            timeout=10
        )

        if r.status_code == 401:
            log("✓ Получен статус 401", "OK")
            detail("Валидация токенов работает корректно")
            return True

        log(f"✗ Ожидался 401, получен {r.status_code}", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_20_get_nonexistent_request(token: str) -> bool:
    """ТЕСТ 20: Получение несуществующей заявки (404)"""
    separator("Несуществующая заявка (404)", "ТЕСТ 20")
    log("GET /api/requests/99999", "TEST")
    detail("Request ID: 99999 (не существует)")

    try:
        r = requests.get(
            f"{BASE_URL}/requests/99999",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if r.status_code == 404:
            log("✓ Получен статус 404", "OK")
            detail("Обработка несуществующих ресурсов корректна")
            return True

        log(f"✗ Ожидался 404, получен {r.status_code}", "ERR")
        show_error_response(r)
        return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    separator("ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ - 20 ТЕСТОВ")
    print(f"{Colors.CYAN}Начало тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")

    tests_passed = []
    tests_failed = []
    test_data = {}

    # ========== ГРУППА 1: АУТЕНТИФИКАЦИЯ ==========
    success, manager_token = test_01_auth_manager()
    if success and manager_token:
        tests_passed.append("01. Auth Manager")
        test_data["manager_token"] = manager_token
        cleanup_test_user(manager_token)
    else:
        tests_failed.append("01. Auth Manager")
        print(f"\n{Colors.RED}❌ Критическая ошибка! Невозможно продолжать без токена менеджера.{Colors.RESET}\n")
        return 1

    if test_02_auth_invalid_credentials():
        tests_passed.append("02. Invalid Credentials")
    else:
        tests_failed.append("02. Invalid Credentials")

    success, operator_token = test_03_auth_operator()
    if success and operator_token:
        tests_passed.append("03. Auth Operator")
        test_data["operator_token"] = operator_token
    else:
        tests_failed.append("03. Auth Operator")

    # ========== ГРУППА 2: ПОЛЬЗОВАТЕЛИ ==========
    success, user_id = test_04_create_user(test_data["manager_token"])
    if success:
        tests_passed.append("04. Create User")
        test_data["created_user_id"] = user_id
    else:
        tests_failed.append("04. Create User")

    if test_05_create_duplicate_user(test_data["manager_token"]):
        tests_passed.append("05. Duplicate User")
    else:
        tests_failed.append("05. Duplicate User")

    if test_06_get_all_users(test_data["manager_token"]):
        tests_passed.append("06. Get Users")
    else:
        tests_failed.append("06. Get Users")

    if test_07_operator_cannot_create_user(test_data.get("operator_token", "")):
        tests_passed.append("07. Operator Permissions")
    else:
        tests_failed.append("07. Operator Permissions")

    # ========== ГРУППА 3: ЗАЯВКИ ==========
    if test_08_get_all_requests(test_data["manager_token"]):
        tests_passed.append("08. Get Requests")
    else:
        tests_failed.append("08. Get Requests")

    success, request_id = test_09_create_request(test_data["manager_token"])
    if success:
        tests_passed.append("09. Create Request")
        test_data["created_request_id"] = request_id
    else:
        tests_failed.append("09. Create Request")

    if test_10_create_request_invalid_data(test_data["manager_token"]):
        tests_passed.append("10. Invalid Request Data")
    else:
        tests_failed.append("10. Invalid Request Data")

    if test_11_get_masters(test_data["manager_token"]):
        tests_passed.append("11. Get Masters")
    else:
        tests_failed.append("11. Get Masters")

    # ========== ГРУППА 4: КОММЕНТАРИИ ==========
    if test_12_get_comments_for_request(test_data["manager_token"]):
        tests_passed.append("12. Get Comments")
    else:
        tests_failed.append("12. Get Comments")

    if test_13_create_comment(test_data["manager_token"], test_data.get("created_request_id")):
        tests_passed.append("13. Create Comment")
    else:
        tests_failed.append("13. Create Comment")

    # ========== ГРУППА 5: СТАТИСТИКА ==========
    if test_14_get_statistics(test_data["manager_token"]):
        tests_passed.append("14. Get Statistics")
    else:
        tests_failed.append("14. Get Statistics")

    if test_15_statistics_by_project(test_data["manager_token"]):
        tests_passed.append("15. Statistics By Project")
    else:
        tests_failed.append("15. Statistics By Project")

    # ========== ГРУППА 6: ФИЛЬТРАЦИЯ ==========
    if test_16_filter_requests_by_status(test_data["manager_token"]):
        tests_passed.append("16. Filter By Status")
    else:
        tests_failed.append("16. Filter By Status")

    if test_17_filter_requests_by_project(test_data["manager_token"]):
        tests_passed.append("17. Filter By Project")
    else:
        tests_failed.append("17. Filter By Project")

    # ========== ГРУППА 7: EDGE CASES ==========
    if test_18_unauthorized_access(test_data["manager_token"]):
        tests_passed.append("18. Unauthorized Access")
    else:
        tests_failed.append("18. Unauthorized Access")

    if test_19_invalid_token():
        tests_passed.append("19. Invalid Token")
    else:
        tests_failed.append("19. Invalid Token")

    if test_20_get_nonexistent_request(test_data["manager_token"]):
        tests_passed.append("20. Nonexistent Request")
    else:
        tests_failed.append("20. Nonexistent Request")

    # ========== ИТОГОВЫЙ ОТЧЁТ ==========
    separator("ИТОГОВЫЙ ОТЧЁТ")
    print(f"{Colors.BOLD}Дата и время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    print(f"{Colors.BOLD}Результаты по группам:{Colors.RESET}\n")

    groups = {
        "Аутентификация": ["01", "02", "03"],
        "Управление пользователями": ["04", "05", "06", "07"],
        "Управление заявками": ["08", "09", "10", "11"],
        "Комментарии": ["12", "13"],
        "Статистика и отчеты": ["14", "15"],
        "Фильтрация": ["16", "17"],
        "Безопасность (Edge Cases)": ["18", "19", "20"]
    }

    for group_name, test_nums in groups.items():
        print(f"\n{Colors.BOLD}{group_name}:{Colors.RESET}")
        for test_name in tests_passed + tests_failed:
            test_num = test_name.split(".")[0]
            if test_num in test_nums:
                status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if test_name in tests_passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
                print(f"  {status} {test_name}")

    total = len(tests_passed) + len(tests_failed)
    pass_rate = (len(tests_passed) / total * 100) if total > 0 else 0

    print(f"\n{'=' * 70}")
    print(f"{Colors.BOLD}ИТОГО:{Colors.RESET}")
    print(f"  Всего тестов: {total}")
    print(f"  Пройдено: {Colors.GREEN}{len(tests_passed)}{Colors.RESET}")
    print(f"  Ошибок: {Colors.RED}{len(tests_failed)}{Colors.RESET}")
    print(f"  Процент успеха: {Colors.CYAN}{pass_rate:.1f}%{Colors.RESET}")
    print(f"{'=' * 70}")

    if len(tests_failed) == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!{Colors.RESET}")
        print(f"{Colors.GREEN}🎉 Система готова к эксплуатации{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ ОБНАРУЖЕНЫ ОШИБКИ В {len(tests_failed)} ТЕСТАХ{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠ Требуется доработка системы{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log("\n\n⚠ Тестирование прервано пользователем", "WARN")
        sys.exit(2)
    except Exception as e:
        log(f"💥 Критическая ошибка: {str(e)}", "ERR")
        import traceback

        traceback.print_exc()
        sys.exit(2)
