from database import db
from sqlalchemy import func


class StatisticsService:

    @staticmethod
    def get_total_requests_count():
        """Всего заявок"""
        try:
            from models.repair_request import RepairRequest
            return RepairRequest.query.count()
        except Exception:
            return 0

    @staticmethod
    def get_masters_count():
        """Количество мастеров"""
        try:
            from models.user import User
            return User.query.filter_by(user_type='Мастер').count()
        except Exception:
            return 0

    @staticmethod
    def get_completed_requests_count():
        """Количество выполненных заявок"""
        try:
            from models.repair_request import RepairRequest
            return RepairRequest.query.filter(
                RepairRequest.request_status.in_(['Готова к выдаче', 'Завершена'])
            ).count()
        except Exception:
            return 0

    @staticmethod
    def get_average_completion_time():
        """Среднее время выполнения заявок в днях"""
        try:
            from models.repair_request import RepairRequest

            requests = RepairRequest.query.filter(
                RepairRequest.completion_date.isnot(None)
            ).all()

            if not requests:
                return 0

            deltas = [
                (r.completion_date - r.start_date).days
                for r in requests
                if r.start_date and r.completion_date
            ]

            if not deltas:
                return 0

            avg_days = round(sum(deltas) / len(deltas), 2)
            return avg_days

        except Exception:
            return 0

    @staticmethod
    def get_statistics_by_equipment_type():
        """Статистика по типам техники"""
        try:
            from models.repair_request import RepairRequest

            equipment_types = db.session.query(
                RepairRequest.tech_type,
                func.count(RepairRequest.request_id).label('total_requests')
            ).group_by(RepairRequest.tech_type).all()

            return [
                {'equipment_type': eq[0] or 'Не указан', 'total_requests': int(eq[1])}
                for eq in equipment_types
            ]

        except Exception:
            return []

    @staticmethod
    def get_master_workload():
        """Нагрузка на мастеров"""
        try:
            from models.repair_request import RepairRequest
            from models.user import User

            masters = db.session.query(User).filter_by(user_type='Мастер').all()
            result = []

            for master in masters:
                active_requests = RepairRequest.query.filter(
                    RepairRequest.master_id == master.user_id,
                    RepairRequest.request_status.in_(['Новая заявка', 'В процессе ремонта', 'Ожидание запчастей'])
                ).count()

                completed_requests = RepairRequest.query.filter(
                    RepairRequest.master_id == master.user_id,
                    RepairRequest.request_status.in_(['Готова к выдаче', 'Завершена'])
                ).count()

                result.append({
                    'master_id': master.user_id,
                    'master_name': master.full_name,
                    'active_requests': int(active_requests),
                    'completed_requests': int(completed_requests),
                    'total_requests': int(active_requests + completed_requests)
                })

            return result

        except Exception:
            return []
