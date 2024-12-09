import json

from load_parameters import get_parameters



class SLBConfiguration:
    """SLB Singleton"""
    config = {}

    @classmethod
    def get_config(cls, section=None):
        if not cls.config:
            parameters = get_parameters()
            config_settings_path = parameters.get("file_paths","config_settings_path")
            file = open(config_settings_path, 'r')
            cls.config = json.load(file)
            file.close()

        if section is not None:
            return cls.__get_section(section)
        else:
            return cls.config

    @classmethod
    def __get_section(cls, section_name):
        return cls.config[section_name]
