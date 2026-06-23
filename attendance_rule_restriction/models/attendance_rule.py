import math
import re
import subprocess
import platform

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import pytz
from datetime import datetime


class AttendanceRule(models.Model):
    _name = 'attendance.rule'
    _description = 'Attendance Rule'
    _order = 'sequence, id'

    name = fields.Char(string='Rule Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    rule_type = fields.Selection([
        ('wifi', 'WiFi'),
        ('ip', 'IP Range'),
        ('geo', 'Geolocation'),
        ('time', 'Time Range'),
        ('device', 'Device'),
    ], string='Rule Type', default='ip', required=True)

    wifi_ids = fields.One2many(
        'attendance.rule.wifi', 'rule_id', string='WiFi List'
    )
    ip_ids = fields.One2many(
        'attendance.rule.ip', 'rule_id', string='IP List'
    )
    geo_ids = fields.One2many(
        'attendance.rule.geo', 'rule_id', string='Location List'
    )
    time_ids = fields.One2many(
        'attendance.rule.time', 'rule_id', string='Time Ranges'
    )

    device_ids = fields.One2many(
        'attendance.rule.device', 'rule_id', string='Allowed Devices'
    )

    # ──────────────────────────────
    # WiFi
    # ──────────────────────────────

    @staticmethod
    def _get_server_wifi():
        system = platform.system()
        ssid = None
        bssid = None
        try:
            if system == 'Windows':
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'interfaces'],
                    capture_output=True, text=True, encoding='utf-8', errors='ignore'
                )
                output = result.stdout
                ssid_match = re.search(r'^\s+SSID\s*:\s*(.+)$', output, re.MULTILINE)
                bssid_match = re.search(
                    r'(?:AP\s+)?BSSID\s*:\s*'
                    r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}'
                    r':[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})',
                    output
                )
                if ssid_match:
                    ssid = ssid_match.group(1).strip()
                if bssid_match:
                    bssid = bssid_match.group(1).strip()

            elif system == 'Darwin':
                result = subprocess.run(
                    ['/System/Library/PrivateFrameworks/Apple80211.framework/'
                     'Versions/Current/Resources/airport', '-I'],
                    capture_output=True, text=True
                )
                output = result.stdout
                ssid_match = re.search(r'^\s+SSID:\s*(.+)$', output, re.MULTILINE)
                bssid_match = re.search(
                    r'BSSID:\s*([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}'
                    r':[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})',
                    output
                )
                if ssid_match:
                    ssid = ssid_match.group(1).strip()
                if bssid_match:
                    bssid = bssid_match.group(1).strip()

            elif system == 'Linux':
                r_ssid = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)
                r_bssid = subprocess.run(['iwgetid', '-a', '-r'], capture_output=True, text=True)
                ssid = r_ssid.stdout.strip() or None
                bssid = r_bssid.stdout.strip() or None
                if not ssid:
                    r = subprocess.run(
                        ['nmcli', '-t', '-f', 'active,ssid,bssid', 'dev', 'wifi'],
                        capture_output=True, text=True
                    )
                    for line in r.stdout.splitlines():
                        parts = line.split(':')
                        if parts[0] == 'yes':
                            ssid = parts[1] if len(parts) > 1 else None
                            bssid = parts[2] if len(parts) > 2 else None
                            break
        except Exception:
            pass
        return ssid, bssid

    # ──────────────────────────────
    # Haversine 距離計算
    # ──────────────────────────────

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # ──────────────────────────────
    # 單條 rule 驗證
    # ──────────────────────────────

    def _validate(self, context_vals):
        self.ensure_one()
        if self.rule_type == 'wifi':
            return self._validate_wifi()
        elif self.rule_type == 'ip':
            return self._validate_ip(context_vals.get('ip'))
        elif self.rule_type == 'geo':
            return self._validate_geo(
                context_vals.get('latitude'),
                context_vals.get('longitude'),
            )
        elif self.rule_type == 'time':
            return self._validate_time(context_vals.get('attendance_type'))
        elif self.rule_type == 'device':
            return self._validate_device()
        return True, ''

    def _validate_wifi(self):
        if not self.wifi_ids:
            return False, _('WiFi rule "%s": No WiFi entries configured.') % self.name

        ssid, bssid = self._get_server_wifi()

        if not ssid and not bssid:
            return False, _(
                'WiFi rule "%s": Cannot detect WiFi on this device.'
            ) % self.name

        # wifi_ids 之間是 OR，任意一條匹配即通過
        for wifi in self.wifi_ids:
            if wifi.bssid:
                if bssid and wifi.bssid.strip().lower() == bssid.strip().lower():
                    return True, ''
            else:
                if ssid and wifi.ssid.strip().lower() == ssid.strip().lower():
                    return True, ''

        return False, _(
            'WiFi rule "%s": No matching WiFi found. Current SSID: %s, BSSID: %s'
        ) % (self.name, ssid or 'N/A', bssid or 'N/A')

    def _validate_ip(self, client_ip):
        import ipaddress

        if not self.ip_ids:
            return False, _('IP rule "%s": No IP entries configured.') % self.name

        if not client_ip:
            return False, _('IP rule "%s": Cannot determine client IP.') % self.name

        # ip_ids 之間是 OR，任意一條匹配即通過
        for ip_entry in self.ip_ids:
            try:
                if ipaddress.ip_address(client_ip) in ipaddress.ip_network(
                    ip_entry.ip_range, strict=False
                ):
                    return True, ''
            except ValueError:
                continue

        return False, _(
            'IP rule "%s": Your IP (%s) is not in any allowed range.'
        ) % (self.name, client_ip)

    def _validate_geo(self, latitude, longitude):
        if not self.geo_ids:
            return False, _('Geo rule "%s": No location entries configured.') % self.name

        if not latitude or not longitude:
            return False, _(
                'Geo rule "%s": Cannot determine your location. '
                'Please allow location access.'
            ) % self.name

        # geo_ids 之間是 OR，任意一條匹配即通過
        for geo in self.geo_ids:
            distance = self._haversine(
                geo.latitude, geo.longitude,
                float(latitude), float(longitude),
            )
            if distance <= geo.radius:
                return True, ''

        # 找出最近的地點提示
        min_dist = min(
            self._haversine(g.latitude, g.longitude, float(latitude), float(longitude))
            for g in self.geo_ids
        )
        return False, _(
            'Geo rule "%s": You are not within any allowed location '
            '(closest is %.0f m away).'
        ) % (self.name, min_dist)

    # ──────────────────────────────
    # 統一驗證入口（rules 之間 AND）
    # ──────────────────────────────

    @api.model
    def validate_all(self, context_vals):
        rules = self.search([('company_id', '=', self.env.company.id)])
        for rule in rules:
            passed, error_msg = rule._validate(context_vals)
            if not passed:
                raise UserError(error_msg)

    def action_add_current_ip(self):
        from odoo.http import request
        current_ip = request.httprequest.remote_addr
        self.env['attendance.rule.ip'].create({
            'rule_id': self.id,
            'name': 'Auto detected',
            'ip_range': current_ip,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'IP Added',
                'message': 'Current IP %s has been added.' % current_ip,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_add_current_geo(self, latitude, longitude):
        self.ensure_one()
        self.env['attendance.rule.geo'].create({
            'rule_id': self.id,
            'name': 'Auto detected',
            'latitude': latitude,
            'longitude': longitude,
            'radius': 200,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Location Added',
                'message': 'Current location (%.6f, %.6f) has been added.' % (latitude, longitude),
                'type': 'success',
                'sticky': False,
            }
        }

    def _validate_time(self, attendance_type):
        if not self.time_ids:
            return False, _('Time rule "%s": No time ranges configured.') % self.name

        # 取員工公司時區
        tz_name = self.env.company.resource_calendar_id.tz or 'UTC'
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        current_time = now.hour + now.minute / 60.0

        # 過濾符合 attendance_type 且今天星期適用的記錄
        applicable = self.time_ids.filtered(
            lambda t: t.attendance_type == attendance_type and t._is_weekday_allowed(weekday)
        )

        if not applicable:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return False, _(
                'Time rule "%s": No time range configured for %s %s.'
            ) % (self.name, day_names[weekday], attendance_type.replace('_', '-'))

        # time_ids 之間是 OR，任意一條匹配即通過
        for t in applicable:
            if t.time_from <= current_time <= t.time_to:
                return True, ''

        # 格式化時間顯示
        def fmt(f):
            h, m = int(f), int(round((f % 1) * 60))
            return '%02d:%02d' % (h, m)

        ranges = ', '.join('%s-%s' % (fmt(t.time_from), fmt(t.time_to)) for t in applicable)
        return False, _(
            'Time rule "%s": Current time %s is not within allowed range(s): %s.'
        ) % (self.name, fmt(current_time), ranges)

    def _validate_device(self):
        from odoo.http import request as http_request

        if not self.device_ids:
            return False, _('Device rule "%s": No device entries configured.') % self.name

        try:
            # 從 request 拿當前設備信息
            user_agent = http_request.httprequest.user_agent
            current_platform = user_agent.platform or ''
            current_browser = user_agent.browser or ''
            current_device_type = 'mobile' if self._is_mobile(current_platform) else 'computer'
        except Exception:
            return False, _('Device rule "%s": Cannot determine device information.') % self.name

        # device_ids 之間是 OR
        for device in self.device_ids:
            # device_type 檢查
            if device.device_type != 'both' and device.device_type != current_device_type:
                continue

            # platform 檢查（填了才比對）
            if device.platform:
                if device.platform.strip().lower() not in current_platform.lower():
                    continue

            # browser 檢查（填了才比對）
            if device.browser:
                if device.browser.strip().lower() not in current_browser.lower():
                    continue

            # 全部條件通過
            return True, ''

        return False, _(
            'Device rule "%s": Your device is not allowed. '
            'Current device: %s %s (%s).'
        ) % (self.name, current_platform or 'Unknown', current_browser or 'Unknown', current_device_type)

    @staticmethod
    def _is_mobile(platform):
        if not platform:
            return False
        mobile_platforms = ['android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone', 'webos']
        return platform.lower() in mobile_platforms