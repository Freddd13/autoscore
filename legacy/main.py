import requests
import feedparser

from datetime import datetime, timedelta
import time
import re
import os
import getpass
import json

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.application import MIMEApplication

import logging
import logging.config


IS_AUTHOR_ENV = (getpass.getuser()=="Fred")
LOG_PATH = "app.log"
LAST_SUCCESS_VAR_NAME = "LAST_SUCCESS_VIDEO_TIME"
# log_file = 'myapp.log'
config_dict = {
    'log_file': LOG_PATH
}
logging.config.fileConfig('logging.conf', defaults=config_dict)
logger = logging.getLogger(__file__)

def log_method(func):
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__
        method_name = func.__name__
        # logger = logging.getLogger(class_name)
        logger.debug(f"{class_name}.{method_name} is called")
        return func(*args, **kwargs)
    return wrapper

def apply_log_method_to_all_methods(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value):
            setattr(cls, attr_name, log_method(attr_value))
    return cls



@apply_log_method_to_all_methods
class MMS:
    def __init__(self, email, password, savefolder_path):
        self.email = email
        self.password = password

        self.login_url = "https://mms.pd.mapia.io/mms/public/user/signin/email"
        self.headers_login = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                #    "X-Api-Key": "mms-public:vslwa5vt0v6E8zfnxwbmw4VFzHCcsgXb5AX7m3Lk",
            "X-Platform-Type": "PC",
            "Referer": "https://www.mymusicsheet.com/",
            "Origin": "https://www.mymusicsheet.com",
        }
        
        if not self.login():
            logger.error("sending err email")
            os._exit()
        
        self.headers_download = {
            'Accept': 'application/json',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Encoding': 'gzip, deflate', # GH不支持br
            'Accept-Language': 'zh-hans',
            "Authorization": f"Bearer {self.auth_token}",
            'Ngsw-Bypass': 'true',
            'Origin': 'https://www.mymusicsheet.com',
            'Referer': 'https://www.mymusicsheet.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        #    'X-Api-Key': 'mms-public:XXX',
            'X-Platform-Type': 'PC',
            # 'X-Sentry-Request-Id': '0uuc5kkkk',
            # 'X-Smp-Version': '4.8.3',
            'X-Viewer-Country': 'cn',
        }

        self.savefolder_path = savefolder_path
        self._file_paths = []
        self._success = True


    def login(self) -> bool:
        payload = {
            "email": self.email,
            "password": self.password
        }

        response = requests.post(self.login_url, json=payload, headers=self.headers_login)

        if response.status_code == 200:
            self.auth_token = json.loads(response.text)['token']
            logger.info("登录成功")
            # logger.info("auth_token: " + self.auth_token)
            return True
        else:
            logger.info("登录失败")
            return False


    def download_sheet(self, num):
        url = 'https://mms.pd.mapia.io/mms/public/sheet/' + num
        response = requests.get(url, headers=self.headers_download)

        if response.status_code != 200:
            logger.error("fail to get sheet data")

        #print(response.text)
        response.encoding = 'utf-8'
        data = response.json()
        # logger.debug(data.keys())

        if not os.path.exists(self.savefolder_path):
            os.makedirs(self.savefolder_path)        
        success_num = 0
        total_num = 0
        for file in data['files']:
            filename = file['fileName']
            if filename.endswith(".pdf"):
                total_num += 1
                mfsKey=file['mfsKey']
                # logger.debug("mfsKey: " + mfsKey)
                #		 GET https://payport.pd.mapia.io/v2/currency?serviceProvider=mms&ngsw-bypass=true&no-cache=1693829884916&skipHeaders=true 
                #		url = "https://payport.pd.mapia.io/v2/currency"
                url_pdf = "https://mms.pd.mapia.io/mms/public/file/" + mfsKey + "/download"

                response_pdf = requests.get(url_pdf, headers=self.headers_download)

                if response_pdf.status_code == 200:
                    # print(response_pdf.text)
                    filepath = os.path.join(self.savefolder_path, filename)
                    with open(filepath, "wb") as file:
                        file.write(response_pdf.content)

                    self._file_paths.append(filepath)
                    success_num += 1
                    logger.info(f"文件 '{filename}' 下载成功")
                else:
                    logger.info(f"请求失败，状态码: {response_pdf.status_code}，错误信息: {response_pdf.text}")
        
        logger.debug(f"success num {success_num} / {total_num} ")
        if success_num != total_num:
            logger.error(f"Some of {num} downloading failed")
            self._success = False
        else:
            logger.info(f"All of {num} downloading success")
            

    def utilize_nums(self, num):
        self.download_sheet(num)

    @property
    def file_paths(self):
        return self._file_paths

    @property
    def success(self):
        return self._success



@apply_log_method_to_all_methods
class EmailHandler:
    def __init__(self, email,smtp_host,smtp_port, mail_license, receivers):
        self.email = email
        self.smtp_host =smtp_host
        self.smtp_port = smtp_port
        self.mail_license = mail_license
        self.receivers = receivers


    def perform_sending(self, subject, content, files=[]):
        message = MIMEMultipart()
        message['From'] = self.email
        message['To'] =  ';'.join(self.receivers)
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # sheet files
        for file in files:
            filename = os.path.basename(file)
            logger.debug("sending filename: "+filename)
            # att = MIMEText(open(file, 'rb').read())
            # att["Content-Type"] = 'application/octet-stream'
            # att["Content-Disposition"] = 'attachment; filename=' + '\"'+ filename +'\"'

            with open(file, "rb") as f:
                #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
                attach = MIMEApplication(f.read(),_subtype="pdf")
            attach.add_header('Content-Disposition','attachment',filename=filename)
            message.attach(attach)

        # log file
        # logger.debug(LOG_PATH)
        # logger.debug(os.getcwd())
        filename = os.path.basename(LOG_PATH)
        att = MIMEText(open(LOG_PATH, 'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename=' + '\"'+ filename +'\"'
        message.attach(att)

        try:
            context=ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, port=self.smtp_port) as smtp:
                smtp.starttls(context=context)
                smtp.login( self.email, self.mail_license)
                smtp.sendmail(self.email, self.receivers, message.as_string())
                logger.info("send email success")

        except Exception as e:
            logger.error(str(e))
            logger.error("无法发送邮件")



@apply_log_method_to_all_methods
class YoutubeRSSHandler:
    def __init__(self, last_success_time = 0.0, max_days_difference = 14, max_trial_num = 10, subers=[], url=""):
        # self.url = "https://rsshub.app/youtube/user/@HalcyonMusic"
        self.max_days_difference = max_days_difference
        self.max_trial_num = max_trial_num
        self._last_success_time = last_success_time
        self._latest_time_str = ""
        # logger.debug(self._last_success_time)
        self.url = url
        self.subers = subers
        self.proxy_dict = {
            'http': '127.0.0.1:51837',
            'https': '127.0.0.1:51837',
        } if IS_AUTHOR_ENV else {}


    def notify_subers(self, num):
        for suber in self.subers:
            suber.utilize_nums(num)

    def get_sheet_number(self):
        response = requests.get(self.url,proxies=self.proxy_dict)

        if response.status_code == 200:
            feed = feedparser.parse(response.text)

            logger.info("Feed Title: " + feed.feed.title)
            # enum rss
            current_tried_num = 0
            for entry in feed.entries:
                if 'published' in entry:
                    published_date_str = entry.published
                    published_date = datetime.strptime(published_date_str, "%a, %d %b %Y %H:%M:%S %Z")

                    # logger.debug(str(published_date.timestamp()) + " " + str(published_date.timestamp() +3600) + " " + str(self._last_success_time)  )
                    logger.debug(f"publish-last {published_date.timestamp() - self._last_success_time}")
                    if published_date.timestamp() <= self._last_success_time:
                        logger.warn("No more sheets")
                        break

                    days_difference = (datetime.now() - published_date).days
                    logger.info("标题:"+entry.title)
                    logger.info("发布日期:"+str(published_date))
                    logger.info("距离当前天数:"+str(days_difference) + "天")
                    if days_difference > self.max_days_difference:
                        logger.warning("距离当前天数超过阈值，跳过")
                        break
                if current_tried_num >= self.max_trial_num:
                    break
                else:
                    current_tried_num += 1

                # print("Entry Title:", entry.title)
                # print("Entry Link:", entry.link)
                # print("Entry Summary:", entry.summary)
                sheet_url_matched = False
                logger.info("-" * 50)

                # get mms link #TODO maybe we can use openai api instead of re
                links = re.findall(r'https://[^\s\n]+', entry.summary)
                for link in links:
                    if "mymusic.st" in link or "mymusicsheet" in link:
                        logger.info("MMS Link:" + link)
                        match = re.search(r'\d+', link)
                        if match:
                            extracted_number = match.group()
                            logger.info("Extracted Number:" + extracted_number)
                            if not self._latest_time_str:
                                logger.debug(f"set latest time to { str(int(published_date.timestamp()))}")
                                self._latest_time_str = str(int(published_date.timestamp()))
                            self.notify_subers(extracted_number)
                            time.sleep(0.5)
                            sheet_url_matched = True

                        else:
                            logger.warning("No number found in the link.")
                        
                    if not sheet_url_matched:
                        logger.warning(str(entry.link) + " not matched")
                        # print(entry.summary)
        else:
            logger.error(f"Failed to retrieve RSS data. Status code: {response.status_code}")

    @property
    def latest_time_str(self):
        return self._latest_time_str


##################### strategies ##################### 
@apply_log_method_to_all_methods
class BaseStrategy:
    def __init__(self):
        self.last_success_video_time = None

    def run(self):
        return NotImplementedError

    def load_config(self):
        return NotImplementedError

    def get_last_success_time(self):
        # 从.last_success_time文件中读取时间
        logger.info(str(os.listdir('.')))
        if os.path.exists('_last_success_time'):
            with open('_last_success_time', 'r') as f:
                self.last_success_video_time =  f.readline()
                logger.info(f"_last_success {self.last_success_video_time}")

    def update_last_success_time(self, latest_time_str):
        # 将时间写入当前目前.last_success_time文件
        with open('_last_success_time', 'w') as f:
            f.write(latest_time_str)


@apply_log_method_to_all_methods
class GithubActionStrategy(BaseStrategy):
    def __init__(self):
        logger.info("Using Github Action Strategy")
        super().__init__()
        self.load_config()
        # self.gh_api = GithubAPI(self._github_repo_token, self._github_owner_repo)
        self.get_last_success_time()

    def load_config(self):
        self.email = os.environ.get('MMS_email')
        self.password = os.environ.get('MMS_password')
        self.savefolder_path = os.environ.get('MMS_savefolder_path')

        self.rss_url = os.environ.get('RSS_url')
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


@apply_log_method_to_all_methods
class DockerStrategy(BaseStrategy):
    def __init__(self):
        logger.info("Using DockerStrategy")
        super().__init__()
        self.load_config()
        self.get_last_success_time()

    def load_config(self):
        import yaml
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        self.email = yaml_data['MMS']['email']
        self.password = yaml_data['MMS']['password']
        self.savefolder_path = yaml_data['MMS']['savefolder_path']

        self.rss_url = yaml_data['RSS']['url']
        self.max_days_difference = yaml_data['RSS']['max_days_difference']
        self.max_trial_num = yaml_data['RSS']['max_trial_num']

        self.enable_email_notify = bool(yaml_data['Email']['enable_email_notify'])
        self.sender = yaml_data['Email']['sender']
        self.receivers = yaml_data['Email']['receivers']
        self.smtp_host = yaml_data['Email']['smtp_host']
        self.smtp_port = yaml_data['Email']['smtp_port']
        self.mail_license = yaml_data['Email']['mail_license']


@apply_log_method_to_all_methods
class LocalStrategy(BaseStrategy):
    def __init__(self):
        logger.info('Using LocalStrategy')
        super().__init__()
        self.load_config()
        self.get_last_success_time()

    def load_config(self):
        import yaml
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        self.email = yaml_data['MMS']['email']
        self.password = yaml_data['MMS']['password']
        self.savefolder_path = yaml_data['MMS']['savefolder_path']

        self.rss_url = yaml_data['RSS']['url']
        self.max_days_difference = yaml_data['RSS']['max_days_difference']
        self.max_trial_num = yaml_data['RSS']['max_trial_num']

        self.enable_email_notify = bool(yaml_data['Email']['enable_email_notify'])
        self.sender = yaml_data['Email']['sender']
        self.receivers = yaml_data['Email']['receivers']
        self.smtp_host = yaml_data['Email']['smtp_host']
        self.smtp_port = yaml_data['Email']['smtp_port']
        self.mail_license = yaml_data['Email']['mail_license']
        

if __name__ == "__main__":
    ## 0. get config
    env = os.environ.get('AUTO_HALCYON_ENV')
    assert env

    if env == "LOCAL":
        strategy = LocalStrategy()
    elif env == "DOCKER":
        strategy = DockerStrategy()
    elif env == "GITHUB_ACTION":
        strategy = GithubActionStrategy()
    else:
        logger.error(f"env error, not support env: {env}")
        os._exit(-1)


    ################################  Run  ################################
    ## 1. get last success time
    last_success_video_time = strategy.last_success_video_time
    logger.debug("main step 1 last_success_video_time: " + str(last_success_video_time))
    if not last_success_video_time:
        last_success_time = (datetime.now() - timedelta(days=365)).timestamp()
        logger.debug("no last")
    else:
        last_success_time = float(last_success_video_time)
        logger.debug("has last")
        # logger.debug(str(last_success_video_time))

    ## 2. start mms handler
    mms = MMS(strategy.email, strategy.password, strategy.savefolder_path)

    ## 3. start RSS handler
    yt_rss = YoutubeRSSHandler(last_success_time=last_success_time, subers=[mms], url = strategy.rss_url)
    yt_rss.get_sheet_number()

    ## 4. check result and prepare mail data
    if mms.success:
        if len(mms.file_paths) > 0: # There are new sheets
            strategy.update_last_success_time(yt_rss.latest_time_str)

            subject = "Successfully downloading Halcyon sheets"
            content = "Success!"
            logger.info("All sheets downloaded successfully")

        else:   # nothing new
            subject = "There's no new sheet of Halcyon"
            content = "Nothing!"
            logger.info("There's no new sheet")

    else:   # download error
        subject = "Failed to download Halcyon sheets"
        content = "Failed..."
        logger.error("Failed to download some sheets")

    ## 5. send email
    if strategy.enable_email_notify:
        email_handler = EmailHandler(strategy.sender, strategy.smtp_host, strategy.smtp_port, strategy.mail_license, strategy.receivers)
        email_handler.perform_sending(subject, content, files=mms.file_paths)



