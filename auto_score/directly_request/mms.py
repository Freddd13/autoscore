'''
Date: 2023-10-23 18:04:14
LastEditors: Kumo
LastEditTime: 2024-09-22 19:12:42
Description: 
'''
from auto_score.utils.proxy_decorator import AUTHOR_PROXY
from ..utils.singleton import SingletonMeta, InstanceRegistry
from ..utils.logger import LoggerManager
from ..utils.base_request import BaseRequest

from datetime import datetime, timezone, timedelta
import time
import os
import json
import requests

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger


@log_manager.apply_log_method_to_all_methods
class MMS(BaseRequest):
    _name = "mms_handler"
    def __init__(self, email, password, local_savefolder):
        super().__init__()
        InstanceRegistry.register_instance(self)
        InstanceRegistry.register_handler_instance(self)
        self.email = email
        self.password = password
        self.local_savefolder = local_savefolder
        if not os.path.exists(self.local_savefolder):
            os.makedirs(self.local_savefolder)

        self.login_url = "https://mms.pd.mapia.io/mms/public/user/signin/email"
        self.headers_login = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                #    "X-Api-Key": "mms-public:vslwa5vt0v6E8zfnxwbmw4VFzHCcsgXb5AX7m3Lk",
            "X-Platform-Type": "PC",
            "Referer": "https://www.mymusicsheet.com/",
            "Origin": "https://www.mymusicsheet.com",
        }

        # 
        self.BASE_URL = 'https://www.mymusicsheet.com'
        self.GRAPHQL_URL = 'https://mms.pd.mapia.io/mms/graphql'
        self.EXCHANGE_RATE_URL = 'https://payport.pd.mapia.io/v2/currency'
        
        if not self.login():
            logger.error("sending err email")
            os._exit(-1)
        
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

        self._files = []
        self._sheet_links = []
        self._success = True


    def login(self) -> bool:
        payload = {
            "email": self.email,
            "password": self.password
        }

        response = self._http.post(self.login_url, json=payload, headers=self.headers_login, proxies=self._proxy_dict)

        if response.status_code == 200:
            self.auth_token = json.loads(response.text)['token']
            logger.info("登录成功")
            # logger.info("auth_token: " + self.auth_token)
            return True
        else:
            logger.info("登录失败")
            return False


    def get_exchange_rates(self):
        params = {
            'serviceProvider': 'mms',
            'ngsw-bypass': 'true',
            'no-cache': str(int(datetime.now().timestamp())),
            'skipHeaders': 'true'
        }
        response = self._http.get(self.EXCHANGE_RATE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return None


    def get_recent_sheets(self, username: str, last_sheetnum: int,  iso='USD', free_only=False):
        entry_links, entry_sheetnums, entry_titles = [], [], []

        # 获取汇率
        rates = self.get_exchange_rates()
        if rates is None:
            raise Exception("Failed to get exchange rates")
        
        # GraphQL 请求
        payload = {
            'operationName': 'loadArtistSheets',
            'query': """
            query loadArtistSheets($data: SheetSearchInput!) {
                sheetSearch(data: $data) {
                    list {
                        productId
                        productType
                        metaSong
                        metaMaker
                        metaMusician
                        metaMemo
                        instruments
                        level
                        price
                        sheetId
                        status
                        author {
                            name
                            artistUrl
                            profileUrl
                        }
                        youtubeId
                        title
                        supportCountry
                        excludeCountries
                        __typename
                    }
                    total
                    current
                    listNum
                }
            }""",
            'variables': {
                'data': {
                    'listNum': 10,
                    'paginate': 'page',
                    'includeChord': None,
                    'includeLyrics': None,
                    'page': 1,
                    'level': None,
                    'instruments': [],
                    'orderBy': {
                        'createdAt': 'DESC'
                    },
                    'isFree': free_only,
                    'category': None,
                    'artistUrl': username,
                    'aggregationKeywords': ['PACKAGE_IDS', 'TAG_IDS', 'INSTRUMENTS', 'SHEET_TYPE', 'INCLUDE_CHORD', 'INCLUDE_LYRICS', 'INSTRUMENTATION', 'LEVEL', 'CATEGORY'],
                    'aggregationKeySize': 20
                }
            }
        }

        response = self._http.post(self.GRAPHQL_URL, json=payload)
        if response.status_code != 200:
            # print(response.text)
            raise Exception("GraphQL request failed")

        sheet_search = response.json().get('data', {}).get('sheetSearch', {}).get('list', [])
        # print(response.json())
        
        items = []
        for item in sheet_search:
            price = float(item.get('price', -1))
            if abs(price) < 1e-6: # free sheet
            # if 1: # free sheet
                title = f"{item['author']['name']} | {item['title']}"
                link = f"{self.BASE_URL}/{username}/{item['sheetId']}"
                this_sheetnum = int(link.split("/")[-1])
                if this_sheetnum <= last_sheetnum:
                    logger.warn("Nothing new")
                    break                
                # print('title:', title)
                # print('link:', link)
                # print('sheetnum:', this_sheetnum)
                entry_links.append(link)
                entry_sheetnums.append(this_sheetnum)
                entry_titles.append(title)
                      
        return entry_links, max(entry_sheetnums) if entry_sheetnums else 0, entry_titles


    def download_sheet(self, mms_link:str) -> bool:
        num = mms_link.split("/")[-1]
        url = f'https://mms.pd.mapia.io/mms/public/sheet/{num}'
        response = self._http.get(url, headers=self.headers_download, proxies=self._proxy_dict)

        if response.status_code != 200:
            logger.error("fail to get sheet data")

        #print(response.text)
        response.encoding = 'utf-8'
        data = response.json()
        # logger.debug(data.keys())
  
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
                url_pdf = f"https://mms.pd.mapia.io/mms/public/file/{mfsKey}/download"
                self._sheet_links.append(url_pdf)

                response_pdf = self._http.get(url_pdf, headers=self.headers_download, proxies=self._proxy_dict)

                if response_pdf.status_code == 200:
                    filepath = os.path.join(self.local_savefolder, filename)
                    with open(filepath, "wb") as file:
                        file.write(response_pdf.content)
                    self._files.append(filepath)
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
        return self._success
            

    def download_sheets(self, mms_links:list) -> bool:
        for link in mms_links:
            if not self.download_sheet(link):
                logger.error(f"Fail to download {link}")
                self._success = False
        return self._success
           

    @property
    def file_paths(self):
        return self._files

    @property
    def success(self):
        return self._success

    @property
    def sheet_links(self):
        return self._sheet_links
