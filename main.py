import requests
import feedparser

from datetime import datetime
import json
import time
import re
import os

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.application import MIMEApplication

import logging
import logging.config


IS_LOCAL_ENV = (os.getlogin()=="Fred")
# 从配置文件加载日志设置
logging.config.fileConfig('logging.conf')
LOG_PATH = "app.log"
# logging.basicConfig(level=logging.INFO, filename=LOG_PATH, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app")
def log_method(func):
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__  # 获取类名
        method_name = func.__name__  # 获取方法名
        logger = logging.getLogger(class_name)
        logger.debug(f"{class_name}.{method_name} 被调用")
        return func(*args, **kwargs)
    return wrapper

# 定义一个类装饰器，应用于类的所有方法
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

        # 登录接口URL
        self.login_url = "https://mms.pd.mapia.io/mms/public/user/signin/email"
        self.headers_login = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                #    "X-Api-Key": "mms-public:vslwa5vt0v6E8zfnxwbmw4VFzHCcsgXb5AX7m3Lk",
            "X-Platform-Type": "PC",
            "Referer": "https://www.mymusicsheet.com/",
            "Origin": "https://www.mymusicsheet.com",
            # 可能需要其他头信息，根据实际情况添加
        }
        
        if not self.login():
            logger.error("sending err email")
            #结束程序
            os._exit()
        
        self.headers_download = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
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


    def login(self) -> str:
        payload = {
            "email": self.email,
            "password": self.password
        }

        response = requests.post(self.login_url, json=payload, headers=self.headers_login)

        # 检查响应状态码
        if response.status_code == 200:
            self.auth_token = json.loads(response.text)['token']
            logger.info("登录成功")
            logger.info("auth_token: " + self.auth_token)
            return True
        else:
            logger.info("登录失败")
            return False


    def download_sheet(self, num):
        url = 'https://mms.pd.mapia.io/mms/public/sheet/' + num
        response = requests.get(url, headers=self.headers_download)

        #print(response.text)
        data = json.loads(response.text)

        if not os.path.exists(self.savefolder_path):
            os.makedirs(self.savefolder_path)        
        success_num = 0
        total_num = 0
        for file in data['files']:
            filename = file['fileName']
            if filename.endswith(".pdf"):
                total_num += 1
                mfsKey=file['mfsKey']
                logger.info("mfsKey: " + mfsKey)
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
    def __init__(self, max_days_difference = 14, max_trial_num = 10, suber=[], url=""):
        # self.url = "https://rsshub.app/youtube/user/@HalcyonMusic"
        self.max_days_difference = max_days_difference
        self.max_trial_num = max_trial_num
        self.suber = suber
        self.url = url
        self.proxy_dict = {
            'http': '127.0.0.1:51837',
            'https': '127.0.0.1:51837',
        } if IS_LOCAL_ENV else {}


    def notify_subers(self, num):
        for suber in self.suber:
            suber.utilize_nums(num)

    def get_sheet_number(self):
        response = requests.get(self.url,proxies=self.proxy_dict)

        if response.status_code == 200:
            feed = feedparser.parse(response.text)

            logger.info("Feed Title: " + feed.feed.title)
            # 遍历 RSS 条目并打印标题和链接
            current_tried_num = 0
            for entry in feed.entries:
                if 'published' in entry:
                    # 发布日期通常以 RFC 2822 或 ISO 8601 格式存储
                    published_date_str = entry.published
                    published_date = datetime.strptime(published_date_str, "%a, %d %b %Y %H:%M:%S %Z")  # 解析为 datetime 对象
                    days_difference = (datetime.now() - published_date).days
                    logger.info("标题:", entry.title)
                    logger.info("发布日期:", published_date)
                    logger.info("距离当前天数:", days_difference, "天")
                    if days_difference > self.max_days_difference:
                        logger.warning("距离当前天数超过阈值，跳过")
                        continue
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
                            self.notify_subers(extracted_number)
                            time.sleep(0.5)
                            sheet_url_matched = True

                        else:
                            logger.warning("No number found in the link.")
                        
                    if not sheet_url_matched:
                        logger.warning(str(entry.link) + " not matched")
                        # print(entry.summary)
        else:
            logger.error("Failed to retrieve RSS data. Status code: " + response.status_code)



if __name__ == "__main__":
    if IS_LOCAL_ENV:
        import yaml
        with open('.localconfig.yaml', 'r') as file:
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        email = yaml_data['MMS']['email']
        password = yaml_data['MMS']['password']
        savefolder_path = yaml_data['MMS']['savefolder_path']

        rss_url = yaml_data['RSS']['url']
        max_days_difference = yaml_data['RSS']['max_days_difference']
        max_trial_num = yaml_data['RSS']['max_trial_num']

        sender = yaml_data['Email']['sender']
        receivers = yaml_data['Email']['receivers']
        smtp_host = yaml_data['Email']['smtp_host']
        smtp_port = yaml_data['Email']['smtp_port']
        mail_license = yaml_data['Email']['mail_license']

    else:
        email = os.environ.get('MMS_email')
        password = os.environ.get('MMS_password')
        savefolder_path = os.environ.get('MMS_savefolder_path')

        rss_url = os.environ.get('RSS_url')
        max_days_difference = os.environ.get('RSS_max_days_difference')
        max_trial_num = os.environ.get('RSS_max_trial_num')

        sender = os.environ.get('Email_sender')
        receivers = os.environ.get('Email_receivers')
        smtp_host = os.environ.get('Email_smtp_host')
        smtp_port = os.environ.get('Email_smtp_port')
        mail_license = os.environ.get('Email_mail_license')
        
    # GO!
    mms = MMS(email, password, savefolder_path)

    yt_rss = YoutubeRSSHandler(suber=[mms], url = rss_url)
    yt_rss.get_sheet_number()

    email_handler = EmailHandler(sender, smtp_host, smtp_port,mail_license,receivers)

    if mms.success:
        subject = "Successfully downloading Halcyon sheets"
        content = "Success!"
        logger.info("All sheets downloaded successfully")

    else:
        subject = "Failed to download Halcyon sheets"
        content = "Failed..."
        logger.error("Failed to download some sheets")

    email_handler.perform_sending(subject, content, files=mms.file_paths)

#TODO
#2. GH自动存储和更新上一次数据
