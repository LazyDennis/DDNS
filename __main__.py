import subprocess
import re
import config
from config import PATTERN, COMMAND, TOKEN, DOMAIN, SUB_DOMAIN
from DnspodApi import DnspodApi

def GetRemoteIpAddrs(_dnspod : DnspodApi,sub_domain: str, 
                    record_type: str = config.IPV6, **kwargs):
    ret, record_list = _dnspod.UpdateRecordList(sub_domain=sub_domain, 
                                                record_type=record_type,
                                                **kwargs)
    ipaddrs = []                            
    if ret['code'] == '1'and record_list:
        for record in record_list:
            ipaddrs.append(record['value'])
    return ipaddrs


def GetLocalIpAddrs(_command, _pattern):
    ret, val = subprocess.getstatusoutput(_command)
    ipaddrs = re.findall(_pattern, val)
    return ipaddrs

def TestIp(_target_ip : str):
    TEST_COMMAND = r'ping ' + _target_ip[:_target_ip.rfind(':') + 1:] + '1'
    ret, val = subprocess.getstatusoutput(TEST_COMMAND)
    res = re.findall(r'Lost = (\d)',val)
    return res != '4'
    

def main():
    dnspod = DnspodApi(DOMAIN, TOKEN)
    local_ipaddrs = GetLocalIpAddrs(COMMAND, PATTERN)
    try:
        remote_ipaddrs = GetRemoteIpAddrs(dnspod, SUB_DOMAIN)
    except Exception as e:
        print(e)

    for local_ip in local_ipaddrs:
        if local_ip in remote_ipaddrs:
            print("Remote IP Address is the same the local's.")
            exit(0)
        elif TestIp(local_ip):
            break
        else:
            local_ip = None
                

    # ret, record_list = dnspod.UpdateRecordList(sub_domain=SUB_DOMAIN)
    if local_ip:
        print('Local ip is: ', local_ip)
        record_list = dnspod.GetRecordList()
        print(record_list)

        for record in record_list:
            if record['type'] == config.IPV6:
                ret, res = dnspod.UpdateDns(record_id=record['id'], 
                                            record_line_id=record['line_id'],
                                            sub_domain=SUB_DOMAIN,
                                            value=local_ip
                                            )  
                print(ret, res)
    else:
        print('No available local ip.')

if __name__ == '__main__':
    main()