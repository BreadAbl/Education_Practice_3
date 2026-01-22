from database import db
from datetime import datetime


class RepairRequest(db.Model):
    __tablename__ = 'repair_requests'

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    tech_type = db.Column(db.String(100), nullable=False)
    tech_model = db.Column(db.String(150), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    request_status = db.Column(db.String(50), nullable=False)
    completion_date = db.Column(db.Date)
    repair_parts = db.Column(db.String(255))
    master_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def to_dict(self):
        return {
            'request_id': self.request_id,
            'start_date': str(self.start_date) if self.start_date else None,
            'tech_type': self.tech_type,
            'tech_model': self.tech_model,
            'problem_description': self.problem_description,
            'request_status': self.request_status,
            'completion_date': str(self.completion_date) if self.completion_date else None,
            'repair_parts': self.repair_parts,
            'master_id': self.master_id,
            'client_id': self.client_id
        }
