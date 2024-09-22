'''
Date: 2023-10-23 23:09:59
LastEditors: Kumo
LastEditTime: 2024-09-22 19:45:46
Description: 
'''

from .proxy_decorator import AUTHOR_PROXY

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class BaseRequest:
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
        self._proxy_dict = AUTHOR_PROXY


