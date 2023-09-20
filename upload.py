'''
Date: 2023-09-20 22:55:49
LastEditors: yxt
LastEditTime: 2023-09-20 22:55:49
Description: 
'''

#TODO upload methods
class BaseUploader:
    def __init__(self):
        pass

    def upload(self, file_path):
        return NotImplementedError

class ODUploader:
    def __init__(self):
        pass

    def upload(self, file_path):
        return NotImplementedError

class GDUploader:
    def __init__(self):
        pass

    def upload(self, file_path):
        return NotImplementedError