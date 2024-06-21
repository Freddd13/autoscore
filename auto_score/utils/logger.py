import logging
import os
import colorlog

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
        
        # 创建一个formatter（无时间和路径）
        file_formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
        
        # 创建一个彩色formatter
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(levelname)s] %(message)s',
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        
        # 为handler设置formatter
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
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
