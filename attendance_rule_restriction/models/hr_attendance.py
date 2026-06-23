from odoo import _, api, fields, models


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    # 打卡時記錄 WiFi 信息，方便審計
    wifi_ssid = fields.Char(string='WiFi SSID', readonly=True)
    wifi_bssid = fields.Char(string='WiFi BSSID', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self.env['attendance.rule'].validate_all({
                'wifi_ssid': vals.get('wifi_ssid'),
                'wifi_bssid': vals.get('wifi_bssid'),
            })
        return super().create(vals_list)

    def write(self, vals):
        if 'check_in' in vals or 'check_out' in vals:
            for rec in self:
                self.env['attendance.rule'].validate_all({
                    'wifi_ssid': vals.get('wifi_ssid', rec.wifi_ssid),
                    'wifi_bssid': vals.get('wifi_bssid', rec.wifi_bssid),
                })
        return super().write(vals)