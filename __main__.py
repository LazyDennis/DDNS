import subprocess
import re
from config import PATTERN, COMMAND, TOKEN, DOMAIN, SUB_DOMAIN
from DnspodApi import DnspodApi




def GetIpAddr(_command, _pattern):
    ret, val = subprocess.getstatusoutput(_command)
    ipaddrs = re.findall(_pattern, val)
    if len(ipaddrs):
        ipaddr = ipaddrs[0]
    else:
        ipaddr = None

    return ipaddr

def main():
    ipaddr = GetIpAddr(COMMAND, PATTERN)
    dnspod = DnspodApi(DOMAIN, TOKEN)
    res = dnspod.UpdateDns(ipaddr, SUB_DOMAIN)
    if res:
        print(res)
    else:
        print('no return')

if __name__ == '__main__':
    main()