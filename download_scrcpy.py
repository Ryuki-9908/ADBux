import os
import zipfile
import urllib.request
from pathlib import Path

from core.context import Context


class DownloadScrcpy():
    def __init__(self):
        context = Context(class_name=self.__class__.__name__)
        self.version = context.setting.get("Settings", "scrcpy_ver")
        self.dir_name = "scrcpy"
        exe_dir_name = f"scrcpy-win64-{self.version}"
        self.zip_name = f"{exe_dir_name}.zip"
        fqdn = context.setting.get("Settings", "scrcpy_url")
        self.url = f"{fqdn}/{self.version}/{self.zip_name}"

        exe_dir_name = Path(os.getcwd()).joinpath(self.dir_name, exe_dir_name)
        print(exe_dir_name)
        context.setting.set(section="Settings", key=context.config.SCRCPY_DIR_KEY, value=str(exe_dir_name))

    def download_scrcpy(self):
        print("scrcpy downloading...")
        print(self.url)
        urllib.request.urlretrieve(self.url, self.zip_name)
        print("download finish.")

    def extract_scrcpy(self):
        print("scrcpy unzip...")
        with zipfile.ZipFile(self.zip_name, 'r') as zip_ref:
            zip_ref.extractall(self.dir_name)
        print("unzip finish.")

    def get_scrcpy_path(self):
        exe_path = os.path.join(self.dir_name, f"scrcpy-win64-{self.version}", "scrcpy.exe")
        return exe_path if os.path.exists(exe_path) else None

    def download(self):
        scrcpy_path = self.get_scrcpy_path()

        if not scrcpy_path:
            self.download_scrcpy()
            self.extract_scrcpy()
            scrcpy_path = self.get_scrcpy_path()

            if not scrcpy_path:
                print("scrcpy.exe not found.")
                return

        try:
            os.remove(f".\\{self.zip_name}")
        except Exception as e:
            pass
