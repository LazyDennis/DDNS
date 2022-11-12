import requests


class DnspodApi:

    URL = r'https://dnsapi.cn/'
    API = ('Domain.Info', 'Record.Line.Category', 'Record.List', 'Record.Ddns')

    def __init__(self, _domain: str = '', _token: str = ''):
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
            res = requests.post(self.URL + _api, self.__data)

        import json
        self.__result = json.loads(res.text)

        return self.__result['status'].copy()

    def __Post(self, _mode: int, _target_key_name: str, _target_list: list[dict], 
                _preset_keys: tuple, **kwargs):

        temp_data = self.__data.copy()

        for key in _preset_keys:
            if key in kwargs:
                self.__data[key] = kwargs[key]

        res = self.Post(self.API[_mode])

        if res['code'] == '1' and _target_key_name in self.__result:
            _target_list = self.__result[_target_key_name].copy()

        self.__data = temp_data.copy()

        return res, _target_list

    def UpdateLineList(self, category_names: list[str] = [u'默认']):
        '''
        category_names:     list[str]   线路大类
        '''
        PRESET_KEYS = ['category_names']
        ret, self.__line_list = self.__Post(1, 'data', self.__line_list, PRESET_KEYS, 
                **{PRESET_KEYS[0]: category_names})
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

        ret, self.__record_list = self.__Post(2, 'records', self.__record_list, 
                                                PRESET_KEYS, **kwargs)
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

        record_result : dict = {}

        return self.__Post(3, 'record', record_result, PRESET_KEYS, **kwargs)
