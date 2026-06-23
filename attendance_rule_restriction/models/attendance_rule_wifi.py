import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AttendanceRuleWifi(models.Model):
    _name = 'attendance.rule.wifi'
    _description = 'Attendance Rule WiFi'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        'attendance.rule',
        string='Rule',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Label', help='Optional label for this WiFi entry')
    ssid = fields.Char(string='WiFi Name (SSID)')
    bssid = fields.Char(string='BSSID (MAC Address)')

    @api.constrains('ssid', 'bssid')
    def _check_required(self):
        for rec in self:
            if not rec.ssid and not rec.bssid:
                raise UserError(_('Each WiFi entry requires at least a SSID or BSSID.'))

    @api.constrains('bssid')
    def _check_bssid_format(self):
        pattern = re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
        for rec in self:
            if rec.bssid and not pattern.match(rec.bssid):
                raise UserError(_('BSSID format is invalid. Expected: AA:BB:CC:DD:EE:FF'))