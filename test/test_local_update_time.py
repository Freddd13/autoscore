'''
Date: 2023-09-20 23:46:03
LastEditors: kumo
LastEditTime: 2023-09-20 23:55:50
Description: 
'''
import os
import time
from datetime import datetime, timedelta



def update_last_success_time(latest_time_str):
    # 将时间写入当前目前.last_success_time文件
    with open('.last_success_time', 'w') as f:
        f.write(latest_time_str)


def get_last_success_time():
    # 从.last_success_time文件中读取时间
    if os.path.exists('.last_success_time'):
        with open('.last_success_time', 'r') as f:
            last_success_video_time =  f.readline()
            print(float(last_success_video_time))

if __name__ == '__main__':
    last_success_video_time = (datetime.now() - timedelta(days=365)).timestamp()

    get_last_success_time()
    update_last_success_time(str(
            int(last_success_video_time)
        )   
    )