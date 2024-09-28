"""
Date: 2023-10-23 18:24:31
LastEditors: Kumo
LastEditTime: 2024-09-28 17:21:58
Description: 
"""

from auto_score.deploy_stragegies import *
from auto_score.utils.proxy_decorator import IS_AUTHOR_ENV

from auto_score.utils.singleton import get_instance, get_handler, GetHandlers
from auto_score.utils.logger import LoggerManager
from auto_score.directly_request.mms import MMS

from auto_score.ms_auth import MSAuth
from auto_score.onedrive.patch import upload_large_file
from auto_score.email.email import EmailHandler

import hashlib
import os
import base64

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger
ERROR_MSGS = []


def parse_last_download(lines):
    last_download = {}
    for line in lines:
        md5, timestamp = line.strip().split(" ")
        last_download[md5] = float(timestamp)
    return last_download


def generate_xoauth2(username, token):
    xoauth = "user=%s\x01auth=Bearer %s\x01\x01" % (username, token)
    xoauth = xoauth.encode("ascii")
    xoauth = base64.b64encode(xoauth)
    xoauth = xoauth.decode("ascii")
    # print("XOAUTH2: ", xoauth)
    return xoauth


def collect_errors(err):
    logger.error(err)
    ERROR_MSGS.append(err)


if __name__ == "__main__":
    ## 0. get config
    env = os.environ.get("AUTO_HALCYON_ENV")
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
        collect_errors(f"env error, not support env: {env}")
        os._exit(-1)

    ## 1. Init
    ### website handlers
    mms_handler = MMS(strategy.email, strategy.password, strategy.savefolder_path)

    ### messy params
    sub_filename = "./subscriptions"  # source | user
    last_download_filename = "./_last_download_signal"

    ## 2. load subscriptions and last downloading times
    assert os.path.exists(sub_filename)
    with open(sub_filename, "r", encoding="utf-8") as file:
        subscriptions = file.readlines()
    if os.path.exists(last_download_filename):
        with open(last_download_filename, "r") as file:
            last_download_lines = file.readlines()
        last_downloads = (
            parse_last_download(last_download_lines) if last_download_lines else {}
        )
    else:
        last_download_lines = {}

    ## 3. for each sub, try to find new links in rss data and call cloudreve offline download
    all_tasks_success = True
    num_newly_downloads = 0
    titles_newly_download = []
    latest_downloads = {}
    for sub in subscriptions:
        parts = sub.strip().split("|")
        assert len(parts) >= 2
        source_name = parts[0]
        user = parts[1]

        full_description = "".join(parts)
        md5 = hashlib.md5(full_description.encode("utf-8")).hexdigest()
        last_sheetnum = last_downloads.get(md5, -1)
        latest_downloads[md5] = last_sheetnum

        parser = get_instance(source_name)

        # if parser and parser.is_available:
        handler = get_handler(source_name)
        links, max_sheetnum, titles = handler.get_recent_sheets(
            user, int(last_sheetnum)
        )
        if len(links) > 0:  # only call downloading when having something new
            # if cloudreve.create_directory(folder_to_root_dir): # also ok when folder exists
            print(f"{source_name}_handler")
            is_download_success = handler.download_sheets(links)
            # is_download_success = cloudreve.add_offline_download_task(links, folder_to_root_dir)
            if is_download_success:
                num_newly_downloads += len(links)
                latest_downloads[md5] = max_sheetnum
                titles_newly_download.extend(titles)
                logger.info(
                    f"Successfully download {len(links)} links into {strategy.savefolder_path}."
                )
            else:  # failed when downloading
                all_tasks_success = False
                collect_errors(
                    f"Failed when downloading {user}'s sheets in RSS source {source_name}."
                )

        else:  # nothing new
            logger.warning("No new link found")

        # else:   # failed when getting parser
        #     all_tasks_success = False
        #     collect_errors(f"RSS source {source_name} is not available.")

    ### 4. collect all sheets
    all_sheets_dir = []
    for handler in GetHandlers():
        all_sheets_dir.extend([path for path in handler.file_paths])

    ## 5. upload to onedrive
    if strategy.enable_od_upload:
        od_ms_auth = MSAuth(
            strategy.od_client_id,
            strategy.od_client_secret,
            strategy.od_redirect_uri,
            ["files.readwrite", "user.read", "offline_access"],
            "_od_refresh_token",
        )
        all_od_upload_success = True
        for path in all_sheets_dir:
            if od_ms_auth.get_access_token():
                # get filename from path with extension
                upload_target = os.path.join(
                    strategy.od_upload_dir, os.path.basename(path)
                ).replace("\\", "/")
                logger.debug(upload_target)
                if upload_large_file(od_ms_auth.client, path, upload_target):
                    logger.info("Upload to onedrive successfully")
                else:
                    all_od_upload_success = False
                    collect_errors("Failed to upload to onedrive")
            else:
                collect_errors("cannot refresh onedrive token")

    ## 6. update download data
    with open(last_download_filename, "w") as file:
        for md5, max_sheetnum in latest_downloads.items():
            if max_sheetnum:
                file.write(f"{md5} {max_sheetnum}\n")
        logger.info("Update last download signal successfully.")

    ## 7. send email
    if strategy.enable_email_notify:
        ### check result and prepare mail data
        logger.info("=" * 50)
        logger.info("summary: ")
        has_error_prefix = "[ERROR] " if len(ERROR_MSGS) > 0 else ""
        if all_tasks_success:
            if num_newly_downloads > 0:
                subject = f"{has_error_prefix}Successfully downloading sheets."
                content = "Success downloading the following sheet(s):\n{}".format(
                    "\n".join([title for title in titles_newly_download])
                )
                logger.info("All sheets start to download successfully.")

            else:  # nothing new
                subject = f"{has_error_prefix}There's no new sheet updated."
                content = "There's no new sheet!"
                logger.info("There's no new sheet")

        else:  # download error
            subject = f"{has_error_prefix}Failed to download all sheets."
            content = "Failed..."
            collect_errors("Failed to download all sheets.")

        if has_error_prefix:
            content += "ERROR msgs: \n{}".format("\n".join([err for err in ERROR_MSGS]))
        logger.info("=" * 50)

        if strategy.use_oauth2_outlook:
            ms_auther = MSAuth(
                strategy.outlook_client_id,
                strategy.outlook_client_secret,
                strategy.outlook_redirect_uri,
                ["https://outlook.office.com/SMTP.Send", "offline_access"],
                "_outlook_refresh_token",
            )
            ms_access_token = ms_auther.get_access_token()
            if not ms_access_token:
                os._exit(-1)
            else:
                xoauth = generate_xoauth2(strategy.sender, ms_access_token)
                email_handler = EmailHandler(
                    strategy.sender,
                    strategy.smtp_host,
                    strategy.smtp_port,
                    strategy.mail_license,
                    strategy.receivers,
                    xoauth=xoauth,
                )
        else:
            email_handler = EmailHandler(
                strategy.sender,
                strategy.smtp_host,
                strategy.smtp_port,
                strategy.mail_license,
                strategy.receivers,
            )
        # all_sheets_dir.extend(LoggerManager.get_all_log_filenames())
        try:
            email_handler.perform_sending(
                subject,
                content,
                sheet_files=all_sheets_dir,
                log_files=(
                    LoggerManager.get_all_log_filenames() if strategy.send_logs else []
                ),
            )
        except Exception as e:
            collect_errors(str(e))
            os._exit(-1)

    # make github action failed
