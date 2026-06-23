from odoo import models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _attendance_action_change(self, geo_information=None):
        self.ensure_one()

        attendance_type = 'check_out' if self.attendance_state == 'checked_in' else 'check_in'

        mode = 'manual'
        client_ip = None
        latitude = None
        longitude = None
        clean_geo = {}

        if geo_information:
            mode = geo_information.get('mode', 'manual')
            client_ip = geo_information.get('client_ip')
            latitude = geo_information.get('latitude')
            longitude = geo_information.get('longitude')
            native_keys = {'mode', 'location', 'latitude', 'longitude', 'ip_address', 'browser'}
            clean_geo = {k: v for k, v in geo_information.items() if k in native_keys}

        self.env['attendance.rule'].validate_all({
            'mode': mode,
            'ip': client_ip,
            'latitude': latitude,
            'longitude': longitude,
            'attendance_type': attendance_type,
        })

        return super()._attendance_action_change(geo_information=clean_geo or None)
