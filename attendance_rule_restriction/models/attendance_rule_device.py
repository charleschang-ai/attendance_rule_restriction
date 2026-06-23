from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AttendanceRuleDevice(models.Model):
    _name = 'attendance.rule.device'
    _description = 'Attendance Rule Device'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        'attendance.rule',
        string='Rule',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Label', required=True)
    device_type = fields.Selection([
        ('computer', 'Computer'),
        ('mobile', 'Mobile'),
        ('both', 'Both'),
    ], string='Device Type', default='both', required=True)
    platform = fields.Char(
        string='Platform',
        help='e.g. Windows, Android, iPhone, iPad. Leave empty to allow any platform.',
    )
    browser = fields.Char(
        string='Browser',
        help='e.g. Chrome, Firefox, Safari. Leave empty to allow any browser.',
    )

    @api.constrains('platform', 'browser', 'device_type')
    def _check_fields(self):
        for rec in self:
            if not rec.platform and not rec.browser and rec.device_type == 'both':
                raise UserError(_(
                    'Device rule entry "%s" must specify at least one of: Platform, Browser, or Device Type.'
                ) % rec.name)
