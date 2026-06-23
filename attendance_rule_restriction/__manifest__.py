{
    "name": "Attendance Rule Restriction | GPS geolocation | IP | IP Checkin | IP Checkout | WiFi check in / check out | Multiple locations for check-in | Multi locations",
    'version': '1.1',
    'category': 'Human Resources/Attendances',
    'price': 30,
    'currency': 'USD',
    'summary': "Restrict employee attendance check-in/out by WiFi, IP, Geolocation, Time Range, and Device rules.",
    'description': """
    Attendance Rule Restriction
    ===========================

    This module adds a flexible rule engine to Odoo's native attendance module,
    allowing companies to control when and where employees can check in or out.

    Features
    --------
    * **WiFi Rule** – Only allow check-in when the Kiosk/server is connected to an authorized WiFi network (matched by SSID or BSSID).
    * **IP Range Rule** – Restrict check-in to specific IP addresses or CIDR ranges (ideal for Systray users on the company network).
    * **Geolocation Rule** – Require employees to be within a defined radius of one or more office locations.
    * **Time Range Rule** – Separately configure allowed check-in and check-out time windows per weekday.
    * **Device Rule** – Limit attendance actions to specific device types, platforms, or browsers.

    How It Works
    ------------
    * Each rule has a single type (WiFi / IP / Geo / Time / Device).
    * Multiple entries within a rule use **OR** logic (any match passes).
    * Multiple rules use **AND** logic (all active rules must pass).
    * Rules are company-scoped and can be individually activated or archived.

    Configuration
    -------------
    Go to **Attendances → Attendance Rules** to create and manage rules.
    """,
    'author': 'Don Shan',
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/attendance_rule_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'attendance_rule_restriction/static/src/geolocation/attendance_rule_geo_button.js',
            'attendance_rule_restriction/static/src/geolocation/attendance_rule_geo_button.xml',
        ],
    },
    "images": ["static/description/icon.jpg"],
    'price': 45,
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "OPL-1",
}
