import subprocess
import re
from DnspodApi import DnspodApi


def main():
    global GlobalLogger
    ddns_conf, log_conf = GetConfig()
    GlobalLogger = GetLogger(log_conf)
    platform_setting = GetPlatformSetting(ddns_conf)
    dnspod = DnspodApi(ddns_conf['domain'], ddns_conf['token'], GlobalLogger)
    local_ipaddrs = GetLocalIpAddrs(
        platform_setting['local_ip_getcommand'] + ' ' +
        platform_setting['local_ethernet_device_name'], 
        platform_setting['local_ip_match_pattern'])
    remote_ipaddrs = []
    local_ip : str = ''
    remote_ipaddrs = GetRemoteIpAddrs(dnspod, ddns_conf['sub_domain'])

    if remote_ipaddrs:
        for local_ip in local_ipaddrs:
            if local_ip in remote_ipaddrs:
                GlobalLogger.info("Remote ip address is the same as the local's.")
                GlobalLogger.info('Program terminated.')
                exit(0)
            elif TestIp(platform_setting['local_ip_testcommand'], local_ip):
                break
            else:
                local_ip = None
                

    # ret, record_list = dnspod.UpdateRecordList(sub_domain=SUB_DOMAIN)
    if local_ip:
        GlobalLogger.info('Local ip address is: %s', local_ip)
        record_list = dnspod.GetRecordList()

        for record in record_list:
            ret, res = dnspod.UpdateDns(record_id=record['id'], 
                                            record_line_id=record['line_id'],
                                            sub_domain=ddns_conf['sub_domain'],
                                            value=local_ip
                                            )  
    else:
        GlobalLogger.info('No available local ip.')


def GetConfig(config_file = None):
    import json, os
    from datetime import datetime
    if config_file is None:
        curr_path = __file__[:__file__.rfind('/') + 1:]
        config_file = curr_path + 'config.json'
    ddns_config = None
    log_config = None
    if os.path.exists(config_file):
        with open(config_file, 'r') as fp:
            json_file = fp.read()
            config = json.loads(json_file)
        if 'ddns_conf' in config:
            ddns_config = config['ddns_conf']
        if 'log_conf' in config:
            log_config = config['log_conf']
        return ddns_config, log_config
    else:
        print(datetime.now().strftime("%y/%m/%d %H:%M:%S.%f")[:-3:], 
             ": Config file ", config_file, " does not exists.")
        print(datetime.now().strftime("%y/%m/%d %H:%M:%S.%f")[:-3:], 
              ": Program terminated.")
        exit(0)

def GetLogger(_log_config):
    import logging
    import logging.config

    logging.config.dictConfig(_log_config)
    return logging.getLogger("ddns_info")

def GetPlatformSetting(_ddns_config):
    import sys
    curr_platform = sys.platform
    GlobalLogger.info('Current platform is %s', curr_platform)
    return _ddns_config['platform_setting'][curr_platform]

def GetRemoteIpAddrs(_dnspod : DnspodApi, sub_domain: str, 
                    record_type: str = 'AAAA', **kwargs):
    GlobalLogger.info('Getting remote ip adress for %s', 
                      sub_domain + '.' + _dnspod.GetDomain())
    ret, record_list = _dnspod.UpdateRecordList(sub_domain=sub_domain, 
                                                record_type=record_type,
                                                **kwargs)
    ipaddrs = []                            
    if ret['code'] == '1'and record_list:
        for record in record_list:
            ipaddrs.append(record['value'])    
        GlobalLogger.info('Successfully got remote ip addresses: %s', ipaddrs)
    else:
        GlobalLogger.info('Failed to get remote ip addresses with return code(%s)', ret['code'])
        GlobalLogger.debug('Error message: %s', ret['message'])
    
    return ipaddrs


def GetLocalIpAddrs(_command, _pattern):
    GlobalLogger.info('Getting local ip.')
    GlobalLogger.debug('Using comand (%s) to get local ip.', _command[:-1:])
    ret, val = subprocess.getstatusoutput(_command)
    ipaddrs = None
    if ret == 0:
        ipaddrs = re.findall(_pattern, val)
        GlobalLogger.info('Successfully got local addresses: %s', ipaddrs)
    else:
        GlobalLogger.info('Faield to get local addresses.')
        GlobalLogger.debug('Error message: %s', val)
    return ipaddrs

def TestIp(_command, _target_ip : str):
    GlobalLogger.info('Testing ip: %s', _target_ip)
    test_command = _command + _target_ip[:_target_ip.rfind(':') + 1:] + '1'
    ret, val = subprocess.getstatusoutput(test_command)
    res = re.findall(r'Lost = (\d)',val)
    if res != '4':
        GlobalLogger.info('Ip is valid.')
        return True
    else:
        GlobalLogger.info('Ip is not valid.')
        return False
    

if __name__ == '__main__':
    main()
