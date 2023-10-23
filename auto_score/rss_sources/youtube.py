'''
Date: 2023-10-23 21:27:08
LastEditors: Kumo
LastEditTime: 2023-10-23 21:28:27
Description: 
'''
from ..utils.singleton import SingletonMeta, InstanceRegistry
from ..utils.logger import LoggerManager

import feedparser
from xml.etree import ElementTree as ET

from datetime import datetime, timezone, timedelta
import time
import requests

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

@log_manager.apply_log_method_to_all_methods
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
