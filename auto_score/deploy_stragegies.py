'''
Date: 2023-10-23 18:24:44
LastEditors: Kumo
LastEditTime: 2023-10-24 00:31:17
Description: 
'''
from .utils.logger import LoggerManager
import os

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
        self.max_days_difference = os.environ.get('RSS_max_days_difference')
        self.max_trial_num = os.environ.get('RSS_max_trial_num')

        self.enable_email_notify = bool(os.environ.get('enable_email_notify'))
        self.sender = os.environ.get('Email_sender')
        self.receivers = [os.environ.get('Email_receivers')] # TODO
        self.smtp_host = os.environ.get('Email_smtp_host')
        self.smtp_port = os.environ.get('Email_smtp_port')
        self.mail_license = os.environ.get('Email_mail_license') 

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
        import yaml
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        self.email = yaml_data['MMS']['email']
        self.password = yaml_data['MMS']['password']
        self.savefolder_path = yaml_data['MMS']['savefolder_path']

        self.rss_url = yaml_data['RSS']['url']
        self.rss_url_key = yaml_data['RSS']['key']
        self.max_days_difference = yaml_data['RSS']['max_days_difference']
        self.max_trial_num = yaml_data['RSS']['max_trial_num']

        self.enable_email_notify = bool(yaml_data['Email']['enable_email_notify'])
        self.sender = yaml_data['Email']['sender']
        self.receivers = yaml_data['Email']['receivers']
        self.smtp_host = yaml_data['Email']['smtp_host']
        self.smtp_port = yaml_data['Email']['smtp_port']
        self.mail_license = yaml_data['Email']['mail_license']


@log_manager.apply_log_method_to_all_methods
class LocalStrategy(BaseStrategy):
    def __init__(self):
        logger.info('Using LocalStrategy')
        super().__init__()
        self.load_config()

    def load_config(self):
        import yaml
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        self.email = yaml_data['MMS']['email']
        self.password = yaml_data['MMS']['password']
        self.savefolder_path = yaml_data['MMS']['savefolder_path']

        self.rss_url = yaml_data['RSS']['url']
        self.rss_url_key = yaml_data['RSS']['key']
        self.max_days_difference = yaml_data['RSS']['max_days_difference']
        self.max_trial_num = yaml_data['RSS']['max_trial_num']

        self.enable_email_notify = bool(yaml_data['Email']['enable_email_notify'])
        self.sender = yaml_data['Email']['sender']
        self.receivers = yaml_data['Email']['receivers']
        self.smtp_host = yaml_data['Email']['smtp_host']
        self.smtp_port = yaml_data['Email']['smtp_port']
        self.mail_license = yaml_data['Email']['mail_license']
       