'''
Date: 2023-10-23 18:24:57
LastEditors: Kumo
LastEditTime: 2023-10-23 18:24:57
Description: 
'''
'''
Date: 2023-10-05 11:08:46
LastEditors: Kumo
LastEditTime: 2023-10-05 18:59:45
Description: 
'''
from .utils.logger import LoggerManager
from .utils.proxy_decorator import IS_AUTHOR_ENV

import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

@log_manager.apply_log_method_to_all_methods
class Cloudreve:
    def __init__(self, email, password, url):
        self._email = email
        self._password = password
        self._base_url = url

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


        if not self.login():
            logger.error("login cloudreve failed")


    def login(self):
        login_url = f"{self._base_url}/api/v3/user/session"
        data = {
            "userName": self._email,
            "Password": self._password,
            "captchaCode": ""
        }
        response = self._http.post(login_url, json=data, proxies=self._proxy_dict)
        return response.json().get("code") == 0


    def add_offline_download_task(self, download_links, destination_directory):
        task_url = f"{self._base_url}/api/v3/aria2/url"
        data = {
            "url": download_links,
            "dst": destination_directory
        }
        response = self._http.post(task_url, json=data, proxies=self._proxy_dict)
        logger.info(response.text)
        return response.json().get("code") == 0


    def create_directory(self, path):
        directory_url = f"{self._base_url}/api/v3/directory"
        data = {
            "path": path
        }
        response = self._http.put(directory_url, json=data, proxies=self._proxy_dict)
        logger.info(response.text)
        return response.json().get("code") == 0