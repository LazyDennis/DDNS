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
        self.__line_info: dict = {}
        self.__record_info: dict = {}

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
        return self.__result

    def GetLineInfo(self) -> dict:
        return self.__line_info

    def Post(self, _api: str, _data: dict = None):
        if _data:
            self.__data = _data
            self.__data.update({'format': 'json'})

        if len(_api):
            res = requests.post(self.URL + _api, self.__data)
            
        import json
        self.__result = json.loads(res.text)

        return self.__result

    def __Post(self, _mode: int):
        return self.Post(self.API[_mode])

    def GetLineInfo(self, _line_name: str = u'默认'):
        self.__data.update({'category_names': _line_name})
        self.__Post(1)
        if self.__result:
            self.__line_info.update({
                'line_name':
                self.__result['data'][0]['line_name'],
                'line_id':
                self.__result['data'][0]['line_id']
            })
        self.__data.pop('category_names')

        return self.__result.copy()

    def GetRecordInfo(self, _sub_domain: str = '', _record_type: str = ''):
        if len(_sub_domain):
            self.__data.update({'sub_domain': _sub_domain})
        if _record_type.upper() == 'AAAA' or _record_type.upper() == 'A':
            self.__data.update({'record_type': _record_type})

        self.__Post(2)
        if 'records' in self.__result:
            for key, value in self.__result['records'][0].items():
                self.__record_info.update({key: value})

        if 'sub_domain' in self.__data:
            self.__data.pop('sub_domain')
        if 'record_type' in self.__data:
            self.__data.pop('record_type')

        return self.__result.copy()

    def UpdateDns(self, _IpAddress: str, _sub_domain: str, _record_type: str = '', **kwargs):
        if 'line_name' in kwargs:
            line_name = kwargs['line_name']
        else:
            line_name = u'默认'

        if 'ttl' in kwargs:
            self.__data.update({'ttl' : kwargs['ttl']})

        if not (self.__line_info and \
            'line_id' in self.__line_info and \
            len(self.__line_info['line_id'])):
            res = self.GetLineInfo(line_name)
            if res['status']['code'] != '1':
                return res

        if not (self.__record_info and \
            'record_id' in self.__record_info and \
                len(self.__record_info['record_id'])):
            res = self.GetRecordInfo(_sub_domain, _record_type)
            if res['status']['code'] != '1':
                return res

        self.__data.update({
                'record_id': self.__record_info['id'],
                'record_line': self.__line_info['line_name'],
                'record_line_id': self.__line_info['line_id'],
                'sub_domain': _sub_domain,
                'value': _IpAddress
            })

        self.__Post(3)

        return self.__result.copy()
