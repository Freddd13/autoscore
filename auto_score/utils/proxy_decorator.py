'''
Date: 2023-10-05 12:46:04
LastEditors: Kumo
LastEditTime: 2023-10-23 22:41:54
Description: 
'''
import getpass

IS_AUTHOR_ENV = (getpass.getuser()=="Fred")
AUTHOR_PROXY = {
    'http': '127.0.0.1:51837',
    'https': '127.0.0.1:51837',
} if IS_AUTHOR_ENV else {}