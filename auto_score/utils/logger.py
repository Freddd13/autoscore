'''
Date: 2023-10-23 18:06:56
LastEditors: Kumo
LastEditTime: 2023-10-23 18:06:56
Description: 
'''
'''
Date: 2023-10-05 12:42:59
LastEditors: Kumo
LastEditTime: 2023-10-05 17:24:55
Description: 
'''
import logging.config
import os

class LoggerManager:
    log_dir_prefix = 'log'
    def __init__(self, log_file):
        # 确保日志目录存在
        if not os.path.exists(self.log_dir_prefix):
            os.makedirs(self.log_dir_prefix)
        
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.DEBUG)
        
        # 创建一个handler来写入日志文件
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # 创建一个handler来输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 创建一个formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # 为handler设置formatter
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 为logger添加handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)


    def log_method(self, func):
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__
            method_name = func.__name__
            self.logger.debug(f"{class_name}.{method_name} is called")
            return func(*args, **kwargs)
        return wrapper


    def apply_log_method_to_all_methods(self, cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, self.log_method(attr_value))
        return cls
    

    @staticmethod
    def get_all_log_filenames():
        return [os.path.join(LoggerManager.log_dir_prefix, filename) for filename in os.listdir(LoggerManager.log_dir_prefix) if filename.endswith('.log')]
