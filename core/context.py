from core.config import Config
from core.logger import Logger
from core.setting import Setting


class Context:
    def __init__(self, class_name: str):
        self.config = Config()
        self.logger = Logger(class_name)
        self.setting = Setting(self.config.SETTING_INI)

    def get_logger(self):
        self.logger.get_logger()

    def get_scrcpy_dir(self):
        section = self.config.SETTING_SECTION
        key = self.config.SCRCPY_DIR_KEY
        return self.setting.get(section, key)