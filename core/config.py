import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    DB_PATH: str = "./db/ADBux.sqlite3"
    LOG_DIR = Path(os.getcwd()).joinpath("logs")
    SETTING_INI = Path(os.getcwd()).joinpath("core", "setting.ini")
    SETTING_SECTION = "Settings"
    SCRCPY_DIR_KEY = "scrcpy_dir"
