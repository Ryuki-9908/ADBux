""" config.ini 操作用 """
import configparser
import os

from utils import values


class Settings:
    def __init__(self, config_file=values.config_path):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load()

        # 存在確認するディレクトリパス
        check_dir_path = [self.get(section="Settings", key="screen_save_path")]

        for path in check_dir_path:
            # ログファイルのディレクトリが存在しない場合は作成
            log_dir = os.path.dirname(path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

    def load(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise FileNotFoundError(f"Config file {self.config_file} not found.")

    def save(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)

    def get(self, section, key):
        return self.config.get(section, key)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save()
