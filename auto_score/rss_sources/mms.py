'''
Date: 2023-10-23 18:04:39
LastEditors: Kumo
LastEditTime: 2023-10-24 00:16:58
Description: 
'''
from .base_rss import BaseRSSParser
from ..utils.singleton import SingletonMeta, InstanceRegistry
from ..utils.logger import LoggerManager

import feedparser
from xml.etree import ElementTree as ET

from datetime import datetime, timezone, timedelta
import os
import time
import requests

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger


@log_manager.apply_log_method_to_all_methods
class MMSRSSHandler(BaseRSSParser, metaclass=SingletonMeta):
    _name = "mms"
    def __init__(self, rss_url="https://rsshub.app/", rss_key = ""):
        super().__init__()
        InstanceRegistry.register_instance(self)
        
        self._url = rss_url
        self._is_available = True
        self._feed = None
        self._rss_key = rss_key

        self.test_source()


    @property
    def is_available(self):
        return self._is_available


    def test_source(self):
        pass


    def get_latest_entries(self, user):
        num_pages_to_check = 1  # TODO
        all_items = []
        logger.info("requesting and merging rss data...")
        for i in range(num_pages_to_check):
            key = f"?key={self._rss_key}" if self._rss_key else ""
            url = os.path.join(self._url, f"mymusicsheet/user/sheets/{user}/USD/1{key}").replace('\\', '/')
            print(url)
            response = self._http.get(url,proxies=self._proxy_dict)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall(".//item"):
                    all_items.append(ET.tostring(item, encoding="unicode"))
            else:       
                return None
                
        # merge RSS XML
        merged_rss = f"""
        <rss version="2.0">
        <channel>
            {''.join(all_items)}
        </channel>
        </rss>
        """    
        return feedparser.parse(merged_rss)  


    def get_download_data(self, user, last_sheetnum):  # timestamp-->sheet_num for now
        entry_links, entry_sheetnums, entry_titles = [], [], []
        if not last_sheetnum:
           last_timestamp = -1

        for entry in self.get_latest_entries(user).entries:
            # time_string = "Wed, 04 Oct 2023 08:31:55 -0700"
            # dt = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            # this_timestamp = dt.timestamp()
            # this_timestamp = dt.timestamp()
            this_sheetnum = float(entry.link.split("/")[-1])

            if this_sheetnum <= last_sheetnum:
                logger.warn("Nothing new")
                break
            
            logger.info("标题:"+entry.title)

            # entry_links.append(entry.enclosures[0].href)
            entry_links.append(entry.link)
            entry_sheetnums.append(this_sheetnum)
            entry_titles.append(entry.title)

        return entry_links, max(entry_sheetnums) if entry_sheetnums else 0, entry_titles
