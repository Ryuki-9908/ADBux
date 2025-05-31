import tkinter as tk
import threading
from core.context import Context
import time


class DeviceMonitorService(Context):
    def __init__(self, master):
        super().__init__(self.__class__.__name__)
        self.master = master
        self._stop_event = threading.Event()
        # タイマー初期化
        self.buf_time = time.time()

        """ 監視サービス起動 """
        self.thread_lock = threading.Lock()  # スレッドロックを使用

    def start(self):
        self._stop_event.clear()
        self._loop()

    def stop(self):
        self._stop_event.set()

    def _loop(self, interval=1):
        if self._stop_event.is_set():
            return

        if self.thread_lock.acquire(blocking=False):  # スレッドロックをチェック
            try:
                # 非同期で監視で自動更新
                threading.Thread(target=self.check_connect_device).start()
            finally:
                self.thread_lock.release()  # スレッドロックを解除

        threading.Timer(interval, self._loop).start()

    """ 接続中デバイスを取得 """
    def check_connect_device(self, event=None):
        show_devices = []
        tmp = self.master.device_to_state.copy()
        self.master.device_to_state.clear()
        self.master.device_to_state = self.master.device_handler.get_connect_device()
        for device in self.master.device_to_state.keys():
            if self.master.device_to_state[device] == "offline":
                device = f"{device}({self.master.device_to_state[device]})"
            show_devices.append(device)
        if self.master.device_to_state != tmp:
            self.master.connect_device_list_view.delete(0, tk.END)
            self.master.connect_device_list_view.insert(tk.END, *show_devices)

        # 接続中デバイス数が減った場合はデバイスが切断されたと判断
        if len(tmp) > len(self.master.device_to_state):
            # 各画面に切断通知
            self.master.disconnect_devices = set(self.master.device_to_state.keys()) ^ set(tmp.keys())
            th = threading.Thread(target=self.master.notice_queues)
            th.start()

        if (event is not None) and (self.master.freq_menu is not None):
            self.logger.debug("device list reload button click.")
            save_data = self.master.freq_device_handler.get_all_device()
            self.master.freq_menu.show_list_reload(save_data)
