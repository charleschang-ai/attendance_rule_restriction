from odoo import _, api, fields, models
from odoo.exceptions import UserError
import ipaddress


class AttendanceRuleIp(models.Model):
    _name = 'attendance.rule.ip'
    _description = 'Attendance Rule IP'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        'attendance.rule',
        string='Rule',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Label', help='Optional label for this IP entry')
    ip_range = fields.Char(
        string='IP / CIDR',
        required=True,
        help='e.g. 203.xxx.xxx.xxx or 192.168.1.0/24',
    )

    @api.constrains('ip_range')
    def _check_ip_format(self):
        for rec in self:
            try:
                ipaddress.ip_network(rec.ip_range, strict=False)
            except ValueError:
                raise UserError(_(
                    'IP/CIDR "%s" is invalid. Expected format: 192.168.1.0/24 or 203.xxx.xxx.xxx'
                ) % rec.ip_range)

    @api.model
    def get_current_client_ip(self):
        from odoo.http import request
        return request.httprequest.remote_addr
