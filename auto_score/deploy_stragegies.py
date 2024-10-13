'''
Date: 2023-10-23 18:24:44
LastEditors: Kumo
LastEditTime: 2024-10-13 11:50:38
Description: 
'''
from .utils.logger import LoggerManager
import os
import yaml

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

class RSSSourceConfig:
    def __init__(self, enable, url) -> None:
        self.enable = enable
        self.url = url


@log_manager.apply_log_method_to_all_methods
class BaseStrategy:
    def __init__(self):
        self.last_success_video_time = None
        self.rss = {}

    def run(self):
        return NotImplementedError

    def load_config(self):
        return NotImplementedError


@log_manager.apply_log_method_to_all_methods
class GithubActionStrategy(BaseStrategy):
    def __init__(self):
        logger.info("Using Github Action Strategy")
        super().__init__()
        self.load_config()

    def load_config(self):
        self.email = os.environ.get('MMS_email')
        self.password = os.environ.get('MMS_password')
        self.savefolder_path = os.environ.get('MMS_savefolder_path')

        self.rss_url = os.environ.get('RSS_url')
        self.rss_url_key = os.environ.get('RSS_url_key')

        # email
        ## basic
        self.enable_email_notify = bool(int(os.environ.get('enable_email_notify')))
        self.sender = os.environ.get('Email_sender')
        self.receivers = [os.environ.get('Email_receivers')] # TODO
        self.smtp_host = os.environ.get('Email_smtp_host')
        self.smtp_port = os.environ.get('Email_smtp_port')
        self.mail_license = os.environ.get('Email_mail_license') 
        self.send_logs = os.environ.get('Email_send_logs') 

        ## outlook oauth app params
        self.use_oauth2_outlook = bool(int(os.environ.get('use_oauth2_outlook')))
        self.outlook_client_id = os.environ.get('outlook_client_id')
        self.outlook_client_secret = os.environ.get('outlook_client_secret')
        self.outlook_redirect_uri = os.environ.get('outlook_redirect_uri')

        
        # onedrive
        self.enable_od_upload = bool(int(os.environ.get('enable_od_upload')))
        self.od_client_id = os.environ.get('od_client_id')
        self.od_client_secret = os.environ.get('od_client_secret')
        self.od_redirect_uri = os.environ.get('od_redirect_uri')
        self.od_upload_dir =  os.environ.get('od_upload_dir')

        # private
        # self._github_repo_token = os.environ.get('GITHUB_REPO_TOKEN')
        # self._github_owner_repo = os.environ.get('GITHUB_OWNER_REPO')


@log_manager.apply_log_method_to_all_methods
class DockerStrategy(BaseStrategy):
    def __init__(self):
        logger.info("Using DockerStrategy")
        super().__init__()
        self.load_config()

    def load_config(self):
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)

        # 使用 get 方法来避免 KeyError
        self.email = yaml_data.get('MMS', {}).get('email', None)
        self.password = yaml_data.get('MMS', {}).get('password', None)
        self.savefolder_path = yaml_data.get('MMS', {}).get('savefolder_path', None)

        self.rss_url = yaml_data.get('RSS', {}).get('url', None)
        self.rss_url_key = yaml_data.get('RSS', {}).get('key', None)

        # email
        ## basic
        self.enable_email_notify = bool(yaml_data.get('Email', {}).get('enable_email_notify', False))
        self.sender = yaml_data.get('Email', {}).get('sender', None)
        self.receivers = yaml_data.get('Email', {}).get('receivers', None)
        self.smtp_host = yaml_data.get('Email', {}).get('smtp_host', None)
        self.smtp_port = yaml_data.get('Email', {}).get('smtp_port', None)
        self.mail_license = yaml_data.get('Email', {}).get('mail_license', None)
        self.send_logs = yaml_data.get('Email', {}).get('send_logs', False)

        ## outlook oauth app params
        self.use_oauth2_outlook = bool(yaml_data.get('Email', {}).get('use_oauth2_outlook', False))
        self.outlook_client_id = yaml_data.get('Email', {}).get('outlook_client_id', None)
        self.outlook_client_secret = yaml_data.get('Email', {}).get('outlook_client_secret', None)
        self.outlook_redirect_uri = yaml_data.get('Email', {}).get('outlook_redirect_uri', None)

        # onedrive
        self.enable_od_upload = bool(yaml_data.get('onedrive', {}).get('enable_od_upload', False))
        self.od_client_id = yaml_data.get('onedrive', {}).get('od_client_id', None)
        self.od_client_secret = yaml_data.get('onedrive', {}).get('od_client_secret', None)
        self.od_redirect_uri = yaml_data.get('onedrive', {}).get('od_redirect_uri', None)
        self.od_upload_dir = yaml_data.get('onedrive', {}).get('od_upload_dir', None)    


@log_manager.apply_log_method_to_all_methods
class LocalStrategy(BaseStrategy):
    def __init__(self):
        logger.info('Using LocalStrategy')
        super().__init__()
        self.load_config()

    def load_config(self):
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)

        # 使用 get 方法来避免 KeyError
        self.email = yaml_data.get('MMS', {}).get('email', None)
        self.password = yaml_data.get('MMS', {}).get('password', None)
        self.savefolder_path = yaml_data.get('MMS', {}).get('savefolder_path', None)

        self.rss_url = yaml_data.get('RSS', {}).get('url', None)
        self.rss_url_key = yaml_data.get('RSS', {}).get('key', None)

        # email
        ## basic
        self.enable_email_notify = bool(yaml_data.get('Email', {}).get('enable_email_notify', False))
        self.sender = yaml_data.get('Email', {}).get('sender', None)
        self.receivers = yaml_data.get('Email', {}).get('receivers', None)
        self.smtp_host = yaml_data.get('Email', {}).get('smtp_host', None)
        self.smtp_port = yaml_data.get('Email', {}).get('smtp_port', None)
        self.mail_license = yaml_data.get('Email', {}).get('mail_license', None)
        self.send_logs = yaml_data.get('Email', {}).get('send_logs', False)

        ## outlook oauth app params
        self.use_oauth2_outlook = bool(yaml_data.get('Email', {}).get('use_oauth2_outlook', False))
        self.outlook_client_id = yaml_data.get('Email', {}).get('outlook_client_id', None)
        self.outlook_client_secret = yaml_data.get('Email', {}).get('outlook_client_secret', None)
        self.outlook_redirect_uri = yaml_data.get('Email', {}).get('outlook_redirect_uri', None)

        # onedrive
        self.enable_od_upload = bool(yaml_data.get('onedrive', {}).get('enable_od_upload', False))
        self.od_client_id = yaml_data.get('onedrive', {}).get('od_client_id', None)
        self.od_client_secret = yaml_data.get('onedrive', {}).get('od_client_secret', None)
        self.od_redirect_uri = yaml_data.get('onedrive', {}).get('od_redirect_uri', None)
        self.od_upload_dir = yaml_data.get('onedrive', {}).get('od_upload_dir', None)    


