from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_auth
from models.repair_request import RepairRequest
from models.user import User
from database import db
from datetime import date, datetime

requests_bp = Blueprint('requests', __name__, url_prefix='/api/requests')


@requests_bp.route('/', methods=['GET'])
@require_auth
def get_all_requests(current_user):
    """Получить все заявки с фильтрацией по роли"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        search = request.args.get('search', None)

        query = RepairRequest.query

        # Фильтрация по роли
        if current_user.get('user_type') == 'Заказчик':
            query = query.filter_by(client_id=current_user.get('user_id'))

        if current_user.get('user_type') == 'Мастер':
            query = query.filter_by(master_id=current_user.get('user_id'))

        # Фильтрация по статусу
        if status:
            query = query.filter_by(request_status=status)

        # Поиск по ID
        if search:
            try:
                query = query.filter_by(request_id=int(search))
            except ValueError:
                pass

        # Сортировка по дате (новые первые)
        query = query.order_by(RepairRequest.start_date.desc())

        # Пагинация
        paginated = query.paginate(page=page, per_page=limit, error_out=False)

        # Формирование результата с именами мастеров и клиентов
        result = []
        for req in paginated.items:
            req_dict = req.to_dict()

            # Добавить имя мастера
            if req.master_id:
                master = User.query.get(req.master_id)
                if master:
                    req_dict['master_name'] = master.full_name
            else:
                req_dict['master_name'] = None

            # Добавить имя клиента
            if req.client_id:
                client = User.query.get(req.client_id)
                if client:
                    req_dict['client_name'] = client.full_name
            else:
                req_dict['client_name'] = None

            result.append(req_dict)

        return jsonify({
            'data': result,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requests_bp.route('/<int:request_id>', methods=['GET'])
@require_auth
def get_request(request_id, current_user):
    """Получить одну заявку"""
    try:
        req = RepairRequest.query.get(request_id)

        if not req:
            return jsonify({'error': 'Заявка не найдена'}), 404

        # Проверка доступа для Заказчика
        if current_user.get('user_type') == 'Заказчик' and req.client_id != current_user.get('user_id'):
            return jsonify({'error': 'Доступ запрещен'}), 403

        # Получить данные заявки
        req_dict = req.to_dict()

        # Добавить имя мастера
        if req.master_id:
            master = User.query.get(req.master_id)
            if master:
                req_dict['master_name'] = master.full_name
        else:
            req_dict['master_name'] = None

        # Добавить имя клиента
        if req.client_id:
            client = User.query.get(req.client_id)
            if client:
                req_dict['client_name'] = client.full_name
        else:
            req_dict['client_name'] = None

        return jsonify({'data': req_dict}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@requests_bp.route('/', methods=['POST'])
@require_auth
def create_request(current_user):
    """Создать новую заявку"""
    try:
        allowed_roles = ['Оператор', 'Мастер', 'Менеджер', 'Заказчик']
        if current_user.get('user_type') not in allowed_roles:
            return jsonify({'error': 'Недостаточно прав'}), 403

        data = request.get_json()

        required_fields = ['tech_type', 'tech_model', 'problem_description', 'client_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Отсутствуют обязательные поля'}), 400

        new_request = RepairRequest(
            start_date=date.today(),
            tech_type=data['tech_type'],
            tech_model=data['tech_model'],
            problem_description=data['problem_description'],
            request_status='Новая заявка',
            client_id=data['client_id'],
            master_id=data.get('master_id')
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            'message': 'Заявка успешно создана',
            'request_id': new_request.request_id,
            'request_status': new_request.request_status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requests_bp.route('/<int:request_id>', methods=['PUT'])
@require_auth
def update_request(request_id, current_user):
    """Обновить заявку"""
    try:
        if current_user.get('user_type') not in ['Мастер', 'Менеджер', 'Оператор']:
            return jsonify({'error': 'Недостаточно прав'}), 403

        req = RepairRequest.query.get(request_id)

        if not req:
            return jsonify({'error': 'Заявка не найдена'}), 404

        data = request.get_json()

        # Обновление статуса
        if 'request_status' in data and data['request_status']:
            allowed_statuses = [
                'Новая заявка',
                'В процессе ремонта',
                'Готова к выдаче',
                'Ожидание запчастей',
                'Завершена'
            ]
            if data['request_status'] in allowed_statuses:
                req.request_status = data['request_status']

                # Автоматически установить дату завершения
                if data['request_status'] in ['Завершена', 'Готова к выдаче'] and not req.completion_date:
                    req.completion_date = date.today()

        # Обновление мастера
        if 'master_id' in data:
            req.master_id = data['master_id'] if data['master_id'] else None

        # Обновление запчастей
        if 'repair_parts' in data:
            req.repair_parts = data['repair_parts']

        # Обновление описания проблемы
        if 'problem_description' in data:
            req.problem_description = data['problem_description']

        # Обновление типа техники
        if 'tech_type' in data:
            req.tech_type = data['tech_type']

        # Обновление модели техники
        if 'tech_model' in data:
            req.tech_model = data['tech_model']

        # Ручное обновление даты завершения
        if 'completion_date' in data and data['completion_date']:
            req.completion_date = datetime.fromisoformat(data['completion_date']).date()

        db.session.commit()

        # Вернуть обновленные данные с именами
        req_dict = req.to_dict()

        if req.master_id:
            master = User.query.get(req.master_id)
            if master:
                req_dict['master_name'] = master.full_name

        if req.client_id:
            client = User.query.get(req.client_id)
            if client:
                req_dict['client_name'] = client.full_name

        return jsonify({
            'message': 'Заявка успешно обновлена',
            'data': req_dict
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@requests_bp.route('/<int:request_id>', methods=['DELETE'])
@require_auth
def delete_request(request_id, current_user):
    """Удалить заявку (только Менеджер)"""
    try:
        if current_user.get('user_type') != 'Менеджер':
            return jsonify({'error': 'Только Менеджер может удалять заявки'}), 403

        req = RepairRequest.query.get(request_id)

        if not req:
            return jsonify({'error': 'Заявка не найдена'}), 404

        db.session.delete(req)
        db.session.commit()

        return jsonify({
            'message': 'Заявка успешно удалена',
            'request_id': request_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
