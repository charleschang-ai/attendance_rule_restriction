# netsh wlan show interfaces

import subprocess
result = subprocess.run(
    ['netsh', 'wlan', 'show', 'interfaces'],
    capture_output=True, text=True, encoding='utf-8', errors='ignore'
)
print(result.stdout)
