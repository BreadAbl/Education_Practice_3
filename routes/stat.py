from flask import Blueprint, jsonify
from services.stat_service import StatisticsService

statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')


@statistics_bp.route('/', methods=['GET'])
def get_all_statistics():
    """Получить всю статистику"""
    try:
        total_requests = StatisticsService.get_total_requests_count()
        completed_requests = StatisticsService.get_completed_requests_count()
        avg_days = StatisticsService.get_average_completion_time()
        masters_count = StatisticsService.get_masters_count()
        by_equipment = StatisticsService.get_statistics_by_equipment_type()
        master_workload = StatisticsService.get_master_workload()

        return jsonify({
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'avg_completion_days': avg_days,
            'masters_count': masters_count,
            'equipment_statistics': by_equipment,
            'master_workload': master_workload
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@statistics_bp.route('/completed-count', methods=['GET'])
def get_completed_count():
    """Количество выполненных заявок"""
    return jsonify({'completed_requests_count': StatisticsService.get_completed_requests_count()}), 200


@statistics_bp.route('/average-time', methods=['GET'])
def get_average_time():
    """Среднее время выполнения"""
    return jsonify({'avg_completion_days': StatisticsService.get_average_completion_time()}), 200


@statistics_bp.route('/by-equipment-type', methods=['GET'])
def get_by_equipment_type():
    """Статистика по типам техники"""
    return jsonify(StatisticsService.get_statistics_by_equipment_type()), 200


@statistics_bp.route('/master-workload', methods=['GET'])
def get_master_workload():
    """Нагрузка на мастеров"""
    return jsonify(StatisticsService.get_master_workload()), 200
