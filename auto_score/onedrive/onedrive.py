'''
Date: 2023-10-24 11:00:30
LastEditors: Kumo
LastEditTime: 2023-10-24 13:14:07
Description: 
'''
import microsoftgraph.client

import os
import socket
import re
import requests

from ..utils.logger import LoggerManager
log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

TOKEN_PATH = '_refresh_token'

@log_manager.apply_log_method_to_all_methods
class OnedriveManager:
    def __init__(self, client_id, client_secret, redirect_uri):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._token = None

        self.client = microsoftgraph.client.Client(client_id, client_secret=client_secret, account_type='common')


    def try_refresh_token(self):
        if os.path.exists(TOKEN_PATH):
            refresh_token = open(TOKEN_PATH, 'r').read()
            try:
                self._token =  self.client.refresh_token(self._redirect_uri, refresh_token).data
            except microsoftgraph.exceptions.BaseError as e:
                return False

        else:
            self._token = self._call_user_web_login().data
        
        if 'refresh_token' in self._token:
            open(TOKEN_PATH, 'w').write(self._token['refresh_token'])
            self.client.set_token(self._token)
            return True
        else:
            return False
        

    def _mini_webserver(self):
        HOST = 'localhost'
        PORT = int(self._redirect_uri.split(':')[-1].replace('/', ''))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                return str(data)


    def _call_user_web_login(self):
        scopes=['files.readwrite', 'user.read', 'offline_access']    
        url = self.client.authorization_url(self._redirect_uri, scopes, state=None)

        logger.info("Copy past this url in a browser of your choice")
        logger.info(url)
        #     print("launching url in default browser")
        #     os.startfile(url)
        # and catch the redirect
        response = self._mini_webserver()
        logger.info(repr(response))
        # GET request contains the code in the form
        # code=xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx
        # https://docs.microsoft.com/en-us/graph/auth-v2-user
        code = re.search(r"code=([\w\.-]+)", response).group(1)
        logger.info("Got code", code)
        # code has to be exchanged for the actual token
        token = self.client.exchange_code(self._redirect_uri, code)
        logger.info("Got token")
        return token


    # tmp fix for large files
    def upload_large_file(self,filepath, filename) -> bool:
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filename}:/createUploadSession"
        # tmp headers
        _headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.client.token['access_token']}",
            "Content-Type": "application/json"
        }
        upload_session  = requests.post(url, headers=_headers).json()

        with open(filepath, 'rb') as f:
            data = f.read()
            size = len(data)
            
            chunk_size = 3276800
            for i in range(0, size, chunk_size):
                print(i/size,i,size)
                chunk_data = data[i:i+chunk_size]
                r = requests.put(upload_session['uploadUrl'], headers={'Content-Length': str(len(chunk_data)),
                                'Content-Range': f"bytes {i}-{i+len(chunk_data)-1}/{size}"}, data=chunk_data)
                if r.status_code != 202:
                    break

            if r.status_code == 200 or r.status_code == 201:
                logger.info("Upload success")
                return True
            else:
                logger.error("Upload failed!!!")
                logger.error(r.text)
                return False       
