import os
import subprocess
from ui.error_dialog import ErrorDialog
from utils.log import Log


class Command:
    def __init__(self):
        super(Command, self).__init__()
        class_name = self.__class__.__name__
        self.log = Log(class_name).get_logger()
        self.dialog = ErrorDialog()
        self.error_show = False

    def subprocess_args(self, include_stdout=True):
        if hasattr(subprocess, 'STARTUPINFO'):
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            env = os.environ
        else:
            si = None
            env = None

        if include_stdout:
            ret = {'stdout': subprocess.PIPE}
        else:
            ret = {}
        ret.update({'stdin': subprocess.PIPE,
                    'stderr': subprocess.PIPE,
                    'startupinfo': si,
                    'env': env})
        return ret

    def send_command(self, cmd, result_wait=True, encoding='utf-8', stdout=subprocess.PIPE, subprocess_flag=False, timeout=3):
        if result_wait:
            # 実行結果を待つ場合
            return subprocess.run(cmd, encoding=encoding, stdout=stdout, **self.subprocess_args(subprocess_flag), timeout=timeout)
        else:
            # 実行結果を待たない場合はpopenでコマンド要求
            return subprocess.Popen(cmd, encoding=encoding, stdout=stdout, **self.subprocess_args(subprocess_flag))
