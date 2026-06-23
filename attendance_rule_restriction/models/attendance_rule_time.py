from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AttendanceRuleTime(models.Model):
    _name = 'attendance.rule.time'
    _description = 'Attendance Rule Time Range'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        'attendance.rule',
        string='Rule',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Label', required=True)
    attendance_type = fields.Selection([
        ('check_in', 'Check-in'),
        ('check_out', 'Check-out'),
    ], string='Type', required=True)

    time_from = fields.Float(string='From', required=True)
    time_to = fields.Float(string='To', required=True)

    # 適用星期
    mon = fields.Boolean(string='Mon', default=True)
    tue = fields.Boolean(string='Tue', default=True)
    wed = fields.Boolean(string='Wed', default=True)
    thu = fields.Boolean(string='Thu', default=True)
    fri = fields.Boolean(string='Fri', default=True)
    sat = fields.Boolean(string='Sat', default=False)
    sun = fields.Boolean(string='Sun', default=False)

    @api.constrains('time_from', 'time_to')
    def _check_time_range(self):
        for rec in self:
            if rec.time_from >= rec.time_to:
                raise UserError(_('Time "From" must be earlier than "To".'))
            if rec.time_from < 0 or rec.time_to > 24:
                raise UserError(_('Time must be between 0:00 and 24:00.'))

    @api.constrains('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
    def _check_weekdays(self):
        for rec in self:
            if not any([rec.mon, rec.tue, rec.wed, rec.thu, rec.fri, rec.sat, rec.sun]):
                raise UserError(_('At least one weekday must be selected.'))

    def _is_weekday_allowed(self, weekday):
        """
        weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
        """
        mapping = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        return getattr(self, mapping[weekday], False)