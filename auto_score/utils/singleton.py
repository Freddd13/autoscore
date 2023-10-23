'''
Date: 2023-10-05 12:42:39
LastEditors: Kumo
LastEditTime: 2023-10-23 23:30:18
Description: 
'''
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class InstanceRegistry:
    _registry = {}
    _handler_registry = {}

    @classmethod
    def register_instance(cls, instance):
        class_name = instance.__class__._name
        cls._registry[class_name] = instance

    @classmethod
    def get_instance_by_name(cls, name):
        return cls._registry.get(name)


    @classmethod
    def register_handler_instance(cls, instance):
        class_name = instance.__class__._name
        cls._handler_registry[class_name] = instance

    @classmethod
    def get_handler_instance_by_name(cls, name):
        return cls._handler_registry.get(name)
    
    @classmethod
    def get_handlers(cls):
        return cls._handler_registry.values()


def get_instance(name): #source name
    return InstanceRegistry.get_instance_by_name(name)

def get_handler(name):   #source name
    return InstanceRegistry.get_handler_instance_by_name(f"{name}_handler")

def GetHandlers():
    return InstanceRegistry.get_handlers()