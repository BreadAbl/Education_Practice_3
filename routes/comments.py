from flask import Blueprint, request, jsonify
from middleware.auth_middleware import require_auth
from models.comment import Comment
from models.user import User
from database import db
from datetime import datetime
import traceback

comments_bp = Blueprint('comments', __name__, url_prefix='/api/comments')

@comments_bp.route('/', methods=['POST'])
@require_auth
def create_comment(current_user):
    """Добавить комментарий к заявке"""
    try:
        data = request.get_json()
        print(f"📩 Received comment data: {data}")  # Отладка

        # Проверка обязательных полей
        if not data:
            return jsonify({'error': 'Нет данных в запросе'}), 400

        if 'message' not in data or not data['message']:
            return jsonify({'error': 'Текст комментария обязателен'}), 400

        if 'request_id' not in data:
            return jsonify({'error': 'ID заявки обязателен'}), 400

        # Конвертировать request_id в int
        try:
            request_id = int(data['request_id'])
        except (ValueError, TypeError):
            return jsonify({'error': 'request_id должен быть числом'}), 400

        # Создать новый комментарий (используем текущего пользователя из токена)
        new_comment = Comment(
            message=data['message'],
            master_id=current_user.get('user_id'),
            request_id=request_id
        )

        db.session.add(new_comment)
        db.session.commit()

        # Вернуть данные комментария с именем автора
        user = User.query.get(new_comment.master_id)

        comment_data = {
            'comment_id': new_comment.comment_id,
            'message': new_comment.message,
            'master_id': new_comment.master_id,
            'request_id': new_comment.request_id,
            'created_at': new_comment.created_at.isoformat() if hasattr(new_comment, 'created_at') and new_comment.created_at else datetime.utcnow().isoformat(),
            'master_name': user.full_name if user else 'Неизвестно'
        }

        print(f"✅ Comment created successfully: {comment_data}")  # Отладка

        return jsonify({
            'message': 'Комментарий успешно добавлен',
            'data': comment_data
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating comment: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Ошибка создания комментария: {str(e)}'}), 500


@comments_bp.route('/', methods=['GET'])
@require_auth
def get_comments(current_user):
    """Получить все комментарии к заявке"""
    try:
        request_id = request.args.get('request_id')
        print(f"📥 GET comments for request_id: {request_id}")  # Отладка

        if not request_id:
            return jsonify({'error': 'request_id parameter is required'}), 400

        # Конвертировать в int
        try:
            request_id = int(request_id)
        except ValueError:
            return jsonify({'error': 'request_id must be a number'}), 400

        # Получить комментарии с сортировкой по дате
        # Проверяем, какое поле есть в модели: created_at или comment_date
        if hasattr(Comment, 'created_at'):
            comments = Comment.query.filter_by(request_id=request_id).order_by(Comment.created_at.desc()).all()
        else:
            comments = Comment.query.filter_by(request_id=request_id).all()

        result = []
        for comment in comments:
            # Получить пользователя
            user = User.query.get(comment.master_id)

            comment_data = {
                'comment_id': comment.comment_id,
                'message': comment.message,
                'master_id': comment.master_id,
                'request_id': comment.request_id,
                'created_at': comment.created_at.isoformat() if hasattr(comment, 'created_at') and comment.created_at else None,
                'master_name': user.full_name if user else 'Неизвестно'
            }

            result.append(comment_data)

        print(f"✅ Found {len(result)} comments")  # Отладка

        return jsonify({'data': result}), 200

    except Exception as e:
        print(f"❌ Error in get_comments: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id, current_user):
    """Удалить комментарий (только автор или Менеджер)"""
    try:
        comment = Comment.query.get(comment_id)

        if not comment:
            return jsonify({'error': 'Комментарий не найден'}), 404

        # Проверка прав (только автор или Менеджер может удалить)
        if comment.master_id != current_user.get('user_id') and current_user.get('user_type') != 'Менеджер':
            return jsonify({'error': 'Недостаточно прав для удаления'}), 403

        db.session.delete(comment)
        db.session.commit()

        return jsonify({'message': 'Комментарий успешно удален'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting comment: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500