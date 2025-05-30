import subprocess
import time
from datetime import datetime

from exceptions.adb_exception import NoDeviceSelect
from utils.command import Command
from utils.log import Log


class DeviceHandler:
    def __init__(self):
        super(DeviceHandler, self).__init__()
        class_name = self.__class__.__name__
        # ハンドラの初期化
        self.commander = Command()
        self.log = Log(tag=class_name).get_logger()
        # 接続処理の最大試行回数
        self.connect_max_retry = 5

    """ デバイス切断 """
    def disconnect(self, tar_device) -> bool:
        self.log.debug("device disconnect run.")
        result = False
        if tar_device:
            cmd_result = self.commander.send_command(['adb', '-s', tar_device, 'disconnect'])
            cmd_result = cmd_result.stdout.splitlines()
            if "disconnected" in cmd_result[0]:
                result = True
            else:
                result = False
        return result

    """ デバイス接続 """
    def connect(self, ip_addr, port=''):
        ip_addr_port = ip_addr
        if len(port) > 0:
            ip_addr_port += f":{port}"
        self.log.debug("device connect run.")
        message = ["error", "connect", "already"]
        result_num = 0
        for i in range(self.connect_max_retry):
            cmd_result = self.commander.send_command(['adb', 'connect', ip_addr_port], timeout=5)
            cmd_result = cmd_result.stdout.splitlines()
            connect_response = "connected to {}".format(ip_addr_port)
            if "already" in cmd_result[0]:
                result_num = 2
            elif connect_response in cmd_result[0]:
                result_num = 1

            # 接続成功または済み場合は処理を抜ける
            if result_num > 0: break
        return message[result_num]

    """ 対象デバイスの画面を表示 """
    def view_screen(self, device):
        self.log.debug("scrcpy run.")
        try:
            result = subprocess.run(['./scrcpy/scrcpy.exe', '-s', device], encoding='utf-8', stdout=subprocess.PIPE)
            result = result.stdout.splitlines()
            if [s for s in result if 'ERROR' in s]:
                self.log.error("run scrcpy.exe result error: {}.".format(result))
        except Exception as e:
            self.log.error(e)

    """ 再起動 """
    def reboot(self, device):
        self.log.debug("device reboot command run.")
        self.commander.send_command(['adb', '-s', device, 'reboot'], result_wait=False)
        self.log.debug("reboot command ok.")

    """ シャットダウン """
    def shutdown(self, device):
        self.log.debug("device shutdown command run.")
        self.commander.send_command(['adb', '-s', device, 'reboot', '-p'], result_wait=False)
        self.log.debug("shutdown command ok.")

    """ TimeZone設定 """
    def timezone_setting(self, device):
        self.log.debug("timezone setting command run.")
        is_ok = False
        result = self.commander.send_command(['adb', '-s', device, 'shell', 'setprop', 'persist.sys.timezone', '"Asia/Tokyo"'])
        if result:
            if not result.stdout.splitlines():
                is_ok = True

        if is_ok:
            self.log.debug("timezone setting command ok.")
        else:
            self.log.error("timezone setting command failed.")
        return is_ok

    """ スクリーンショット取得 """
    def screen_shot(self, device):
        self.log.debug("application get screen shot command run.")
        now = datetime.now()
        dt = now.strftime('%Y-%m-%d_%H%M%S%f')

        # 画面キャプチャ撮影
        self.commander.send_command(
            ['adb', '-s', device, 'shell', 'screencap', '-p', '/sdcard/{}_screen.png'.format(dt)],
            result_wait=True, encoding='utf-8', stdout=subprocess.PIPE)
        # スクリーンショットを取得
        self.commander.send_command(
            ['adb', '-s', device, 'pull', '/sdcard/{}_screen.png'.format(dt), './screen_shot/'],
            result_wait=True, encoding='utf-8', stdout=subprocess.PIPE)
        # 端末からスクリーンショットを削除
        self.commander.send_command(
            ['adb', '-s', device, 'shell', 'rm', '-rf', '/sdcard/{}_screen.png'.format(dt)],
            result_wait=False, encoding='utf-8', stdout=subprocess.PIPE)

    """ 接続されたデバイスを取得 """
    def get_connect_device(self):
        device_items = {}
        try:
            result = self.commander.send_command(['adb', 'devices'])
            if result:
                result = result.stdout.splitlines()
                del result[0]
                result.remove("")
                for i in range(len(result)):
                    device, state = result[i].split("\t")
                    # IPアドレス：ポート番号を切り分け
                    # device = device.split(":")[0]
                    device_items[device] = state
        except Exception as e:
            self.log.error(e)

        return device_items

    """ 実行許可を確認 """
    def check_execution(self, tar_device=None, select_only=True):
        device = None
        device_to_state = self.get_connect_device()
        # 辞書からkey(デバイスIP)を取得
        device_items = [device for device in device_to_state.keys()]
        if device_items:
            if (tar_device in device_items) and select_only:
                device = tar_device
            elif not select_only:
                device = device_items[0]
            elif select_only:
                raise NoDeviceSelect

        return device


