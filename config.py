IPV6 = 'AAAA'
IPV4 = 'A'

PATTERN = r'.*inet6 (24.*9)/128' #r'.*(24.*10)'
DEVICE = r'ens160'
COMMAND = r'ip addr show dev ' + DEVICE # r'c:\windows\system32\ipconfig.exe'
PING_COMMAND = r'ping -c 4' # r'c:\windows\system32\ping.exe -n 4'

TOKEN = '301030,6a605eaf3a12cec41f29181cd032887e'
DOMAIN = 'dehomespace.top'
SUB_DOMAIN = 'umini'