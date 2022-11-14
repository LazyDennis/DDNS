import requests
from logging import Logger, getLogger


class DnspodApi:

    URL = r'https://dnsapi.cn/'
    API = ('Domain.Info', 'Record.Line.Category', 'Record.List', 'Record.Ddns')

    def __init__(self, _domain: str = '', _token: str = '', __logger : Logger = None):
        if __logger:
            self.__logger: Logger = __logger
        else:
            self.__logger: Logger = getLogger()
        self.__domain: str = _domain
        self.__token: str = _token
        self.__result: dict = {}
        if self.__domain and self.__token:
            self.__data = {
                'domain': self.__domain,
                'login_token': self.__token,
                'format': 'json'
            }
        self.__line_list: list[dict] = []
        self.__record_list: list[dict] = []

    def SetDomain(self, _domain: str):
        self.__domain = _domain

    def SetToken(self, _token: str):
        self.__token = _token
        return

    def GetDomain(self) -> str:
        return self.__domain

    def GetToken(self) -> str:
        return self.__token

    def GetResult(self) -> dict:
        return self.__result.copy()

    def GetLineList(self) -> dict:
        return self.__line_list

    def GetRecordList(self) -> dict:
        return self.__record_list

    def Post(self, _api: str, _data: dict = None):
        if _data:
            self.__data = _data
            self.__data.update({'format': 'json'})

        if len(_api):
            try:
                self.__logger.debug(
                    'Posting url: %s, data: %s', self.URL + _api, self.__data)
                res = requests.post(self.URL + _api, self.__data)
            except  requests.exceptions.RequestException as e:
                self.__logger.error(e)
                self.__logger.info('Program terminated.')
                exit(0)

        import json
        self.__result = json.loads(res.text)

        return self.__result['status'].copy()

    def __Post(self, _mode: int, _target_key_name: str, _preset_keys: tuple, **kwargs):

        temp_data = self.__data.copy()

        for key in _preset_keys:
            if key in kwargs:
                self.__data[key] = kwargs[key]

        res = self.Post(self.API[_mode])

        if res['code'] == '1' and _target_key_name in self.__result:
            target_list = self.__result[_target_key_name].copy()

        self.__data = temp_data

        return res, target_list

    def UpdateLineList(self, category_names: list[str] = [u'默认']):
        '''
        category_names:     list[str]   线路大类
        '''
        PRESET_KEYS = ['category_names']
        self.__logger.info('Updating line list by %s', category_names)
        ret, self.__line_list = self.__Post(1, 'data', PRESET_KEYS, 
                **{PRESET_KEYS[0]: category_names})
        if ret['code'] == '1':
            self.__logger.info('Update line list successfully.')
        else:
            self.__logger.info('Failed update line list with return code %s', ret['code'])
            self.__logger.debug('Error message: %s', ret['message'])
        return ret, self.__line_list

    def UpdateRecordList(self, **kwargs):
        '''
        offset:         int 	记录开始的偏移。
        length:         int 	共要获取的记录数量的最大值。
        sub_domain:	 	str 	子域名。
        record_type:	str 	记录类型。
        record_line:	str 	记录线路。
        record_line_id:	int 	线路的ID。
        keyword:	 	str 	搜索的关键字。

        '''
        PRESET_KEYS = ('offset', 'length', 'sub_domain',
                       'record_type', 'record_line', 'record_line_id', 'keyword')
        
        self.__logger.info('Updating record list...')
        ret, self.__record_list = self.__Post(2, 'records', PRESET_KEYS, **kwargs)
        
        if ret['code'] == '1':
            self.__logger.info('Update record list successfully.')
        else:
            self.__logger.info('Failed update record list with return code %s', ret['code'])
            self.__logger.debug('Error message: %s', ret['message'])

        return ret, self.__record_list

    def UpdateDns(self, **kwargs):
        '''
        record_id:		    int	记录ID。
        sub_domain:		    str	主机记录。
        record_line:		str	记录线路。
        record_line_id:		str	线路的ID。
        value:		        str	IP 地址
        ttl:		        int	TTL值
        '''
        PRESET_KEYS = ('record_id', 'sub_domain', 'record_line',
                       'record_line_id', 'value', 'ttl')
        
        self.__logger.info('Updating record...')

        ret, record_result = self.__Post(3, 'record', PRESET_KEYS, **kwargs)

        if ret['code'] == '1':
            self.__logger.info('Update record successfully.')
        else:
            self.__logger.info('Failed update line list with return code %s', ret['code'])
            self.__logger.debug('Error message: %s', ret['message'])

        return ret, record_result
