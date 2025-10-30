from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.reports_service import ReportsService
from datetime import datetime, date

ns = Namespace('reports', description='Reports operations')

report_model = ns.model('ReportRequest', {
    'criterion': fields.String(required=True, description='salesperson|product|zone'),
    'start': fields.String(required=True, description='YYYY-MM-DD'),
    'end': fields.String(required=True, description='YYYY-MM-DD'),
})

report_resp = ns.model('ReportResponse', {
    'criterion': fields.String,
    'start': fields.String,
    'end': fields.String,
    'total': fields.Float,
    'pct_change': fields.Float,
    'top5': fields.List(fields.Raw),
    'daily': fields.List(fields.Raw),
})


def role_required(role):
    def deco(f):
        def wrapper(*args, **kwargs):
            # simple stub: read header X-Role
            from flask import request
            r = request.headers.get('X-Role')
            if not r or r != role:
                ns.abort(403, 'forbidden')
            return f(*args, **kwargs)
        return wrapper
    return deco


@ns.route('/reports')
class ReportsResource(Resource):
    @ns.expect(report_model)
    @ns.marshal_with(report_resp)
    def post(self):
        body = request.get_json() or {}
        criterion = body.get('criterion')
        start_s = body.get('start')
        end_s = body.get('end')
        try:
            start = datetime.fromisoformat(start_s).date()
            end = datetime.fromisoformat(end_s).date()
        except Exception:
            ns.abort(400, 'invalid dates')

        svc = ReportsService()
        try:
            r = svc.generate_report(criterion, start, end)
            return r
        except ValueError as e:
            ns.abort(400, str(e))
