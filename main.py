'''
Date: 2023-10-23 18:24:31
LastEditors: Kumo
LastEditTime: 2023-10-23 23:54:43
Description: 
'''
from auto_score.cloudreve import Cloudreve
from auto_score.email import EmailHandler
from auto_score.deploy_stragegies import *
from auto_score.utils.proxy_decorator import IS_AUTHOR_ENV

from auto_score.utils.singleton import get_instance, get_handler, GetHandlers
from auto_score.utils.logger import LoggerManager
from auto_score.rss_sources.mms import MMSRSSHandler
from auto_score.directly_request.mms import MMS

import hashlib
import os

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger


def parse_last_download(lines):
    last_download = {}
    for line in lines:
        md5, timestamp = line.strip().split(' ')
        last_download[md5] = float(timestamp)
    return last_download


if __name__ == "__main__":
    ## 0. get config
    env = os.environ.get('AUTO_HALCYON_ENV')
    if not env and IS_AUTHOR_ENV:
        env = "LOCAL"

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

    ## 1. Init
    ### handlers
    mms_handler = MMS(strategy.email, strategy.password, strategy.savefolder_path)

    ### instances
    # cloudreve = Cloudreve(strategy.email, strategy.password, strategy.url)
    email_handler = EmailHandler(strategy.email, strategy.smtp_host, strategy.smtp_port, strategy.mail_license, strategy.receivers)
    mms_rss = MMSRSSHandler(strategy.rss_url, strategy.rss_url_key)

    ### messy params
    sub_filename = "./subscriptions"    # source | user
    last_download_filename = "./_last_download_signal"
    # cloudreve_download_dir = strategy.download_dir


    ## 2. load subscriptions and last downloading times
    assert(os.path.exists(sub_filename))
    with open(sub_filename, 'r', encoding='utf-8') as file:
        subscriptions =  file.readlines()
    if (os.path.exists(last_download_filename)):
        with open(last_download_filename, 'r') as file:
            last_download_lines =  file.readlines()
        last_downloads = parse_last_download(last_download_lines) if last_download_lines else {}
    else:
        last_download_lines = {}


    ## 3. for each sub, try to find new links in rss data and call cloudreve offline download
    all_tasks_success = True
    num_newly_downloads = 0
    titles_newly_download = []
    latest_downloads = {}
    for sub in subscriptions:
        parts = sub.strip().split('|')
        assert(len(parts) >= 2)
        source_name = parts[0]
        user = parts[1]

        full_description = ''.join(parts)
        md5 = hashlib.md5(full_description.encode('utf-8')).hexdigest()
        last_timestamp = last_downloads.get(md5, -1)
        latest_downloads[md5] = last_timestamp

        parser = get_instance(source_name)
        if parser and parser.is_available:
            # folder_to_root_dir = os.path.join(cloudreve_download_dir, save_folder).replace('\\','/')
            links, max_timestamp, titles = parser.get_download_data(user, last_timestamp)
            if len(links) > 0:  # only call downloading when having something new
                # if cloudreve.create_directory(folder_to_root_dir): # also ok when folder exists
                    handler = get_handler(source_name)
                    print(f"{source_name}_handler")
                    is_download_success = handler.download_sheets(links)
                    # is_download_success = cloudreve.add_offline_download_task(links, folder_to_root_dir)
                    if is_download_success:
                        num_newly_downloads += len(links)
                        latest_downloads[md5] = max_timestamp
                        titles_newly_download.extend(titles)
                        logger.info(f"Successfully download {len(links)} links into {strategy.savefolder_path}.")
                    else:   # failed when downloading
                        all_tasks_success = False
                        logger.error(f"Failed when downloading {user}'s sheets in RSS source {source_name}.")
                # else:       # failed when create folder
                #     all_tasks_success = False
                #     logger.error(f"Failed when create_directory {save_folder} in cloudreve.")
            else:   # nothing new
                logger.warning("No new link found")

        else:   # failed when getting parser
            all_tasks_success = False
            logger.error(f"RSS source {source_name} is not available.")



    ### collect all sheets
    all_sheets_dir = []
    for handler in GetHandlers():
        all_sheets_dir.extend([path for path in handler.file_paths])

    ## 4. check result and prepare mail data
    logger.info("=" * 50)
    logger.info("summary: ")
    if all_tasks_success:
        if num_newly_downloads > 0:
            subject = "Successfully downloading sheets."
            content = "Success downloading the following sheet(s):\n{}".format('\n'.join(str(titles_newly_download)))
            logger.info("All sheets start to download successfully.")

        else:   # nothing new
            subject = "There's no new sheet updated."
            content = "There's no new sheet!"
            logger.info("There's no new sheet")

    else:   # download error
        subject = "Failed to download all sheets."
        content = "Failed..."
        logger.error("Failed to download all sheets.")
    logger.info("=" * 50)


    ## 5. send email
    if strategy.enable_email_notify:
        email_handler = EmailHandler(strategy.sender, strategy.smtp_host, strategy.smtp_port, strategy.mail_license, strategy.receivers)
        # all_sheets_dir.extend(LoggerManager.get_all_log_filenames())
        email_handler.perform_sending(subject, content, sheet_files=all_sheets_dir, log_files=LoggerManager.get_all_log_filenames())

    ## 6. update download data
    with open(last_download_filename, 'w') as file:
        for md5, timestamp in latest_downloads.items():
            if timestamp:
                file.write(f'{md5} {timestamp}\n')