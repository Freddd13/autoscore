'''
Date: 2023-09-20 22:55:49
LastEditors: Kumo
LastEditTime: 2023-09-29 15:34:20
Description: 
'''

#TODO upload methods
class BaseUploader:
    def __init__(self):
        pass

    def upload(self, file_path):
        return NotImplementedError

class ODUploader(BaseUploader):
    def __init__(self):
        pass

    def upload(self, file_path):
        return NotImplementedError

class GDUploader(BaseUploader):
    def __init__(self):
        pass

    def upload(self, file_path):
        return NotImplementedError