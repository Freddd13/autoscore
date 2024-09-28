"""
Date: 2023-10-24 11:00:30
LastEditors: Kumo
LastEditTime: 2024-09-28 17:17:02
Description: 
"""

import microsoftgraph.client

import os
import socket
import re
import requests

from ..utils.logger import LoggerManager

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger


# patch
def upload_large_file(access_token, filepath, filename) -> bool:
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filename}:/createUploadSession"
    # tmp headers
    _headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    upload_session = requests.post(url, headers=_headers).json()
    # print(upload_session)

    with open(filepath, "rb") as f:
        data = f.read()
        size = len(data)

        chunk_size = 3276800
        for i in range(0, size, chunk_size):
            print(i / size, i, size)
            chunk_data = data[i : i + chunk_size]
            r = requests.put(
                upload_session["uploadUrl"],
                headers={
                    "Content-Length": str(len(chunk_data)),
                    "Content-Range": f"bytes {i}-{i+len(chunk_data)-1}/{size}",
                },
                data=chunk_data,
            )
            if r.status_code != 202:
                break

        if r.status_code == 200 or r.status_code == 201:
            logger.info("Upload success")
            return True
        else:
            logger.error("Upload failed!!!")
            logger.error(r.text)
            return False
