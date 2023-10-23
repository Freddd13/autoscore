'''
Date: 2023-10-23 18:22:35
LastEditors: Kumo
LastEditTime: 2023-10-23 18:22:36
Description: 
'''
'''
Date: 2023-10-05 11:10:17
LastEditors: Kumo
LastEditTime: 2023-10-05 18:24:55
Description: 
'''

from ..utils.proxy_decorator import IS_AUTHOR_ENV

import feedparser
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class BaseRSSParser:
    def __init__(self):
        self._retry_strategy = Retry(
            total=5, 
            backoff_factor=1, 
            status_forcelist=[429, 500, 502, 503, 504], 
            allowed_methods=["HEAD", "GET", "OPTIONS"]  
        )

        self._adapter = HTTPAdapter(max_retries=self._retry_strategy)
        self._http = requests.Session()
        self._http.mount("https://", self._adapter)
        self._http.mount("http://", self._adapter)
        self._proxy_dict = {
            'http': '127.0.0.1:51837',
            'https': '127.0.0.1:51837',
        } if IS_AUTHOR_ENV else {}

    @classmethod
    def get_all_instances(cls):
        return list(cls._instances)


    def get_latest_entries(self):
        return NotImplementedError
    

    def get_download_data(self):
        return NotImplementedError
