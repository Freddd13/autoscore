'''
Date: 2023-10-24 11:00:30
LastEditors: Kumo
LastEditTime: 2024-09-28 17:10:09
Description: New oauth2 method to send smtp mail with outlook (https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth)
'''
import microsoftgraph.client

import os
import socket
import re

from auto_score.utils.logger import LoggerManager
log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

TOKEN_PATH = '_outlook_refresh_token'

@log_manager.apply_log_method_to_all_methods
class MSAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._token = None

        self.client = microsoftgraph.client.Client(client_id, client_secret=client_secret, account_type='common')


    def get_access_token(self):
        if os.path.exists(TOKEN_PATH):
            refresh_token = open(TOKEN_PATH, 'r').read()
            try:
                self._token =  self.client.refresh_token(self._redirect_uri, refresh_token).data
            except microsoftgraph.exceptions.BaseError as e:
                logger.error(str(e))
                return False

        else:
            self._token = self._call_user_web_login().data
        
        if 'refresh_token' in self._token:
            open(TOKEN_PATH, 'w').write(self._token['refresh_token'])
            self.client.set_token(self._token)
            return self.client.token['access_token']
        else:
            return None
        

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
        scopes=['https://outlook.office.com/SMTP.Send', 'offline_access']
        url = self.client.authorization_url(self._redirect_uri, scopes, state=None)

        logger.info("Copy past this url in a browser of your choice")
        logger.info(url)
        #     print("launching url in default browser")
        #     os.startfile(url)
        # and catch the redirect
        response = self._mini_webserver()
        logger.info(response)
        # GET request contains the code in the form
        # code=xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx
        # https://docs.microsoft.com/en-us/graph/auth-v2-user
        code = re.search(r"code=([\w\.-]+)", response).group(1)
        # logger.info("Got code", str(code))
        # code has to be exchanged for the actual token
        token = self.client.exchange_code(self._redirect_uri, code)
        logger.info("Got token")
        return token