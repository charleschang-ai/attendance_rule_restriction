from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AttendanceRuleGeo(models.Model):
    _name = 'attendance.rule.geo'
    _description = 'Attendance Rule Geolocation'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        'attendance.rule',
        string='Rule',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Location Name', required=True)
    latitude = fields.Float(string='Latitude', digits=(10, 7), required=True)
    longitude = fields.Float(string='Longitude', digits=(10, 7), required=True)
    radius = fields.Float(
        string='Allowed Radius (m)',
        default=200,
        required=True,
    )

    @api.constrains('radius')
    def _check_radius(self):
        for rec in self:
            if rec.radius <= 0:
                raise UserError(_('Radius must be greater than 0.'))