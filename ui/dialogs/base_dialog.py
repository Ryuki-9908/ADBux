import threading
import tkinter as tk
from db.handlers.freq_device_handler import FreqDeviceHandler
from utils.command import Command
from ui.handlers.device_handler import DeviceHandler
from ui.handlers.json_handler import JsonHandler
from core.context import Context


class BaseDialog(tk.Frame):
    def __init__(self, dialog, screen_id, que_key, que, close_callback):
        super().__init__(dialog)

        """ 初期化処理 """
        self.dialog = dialog
        self.screen_id = screen_id
        self.que_key = que_key

        # メインスレッドからの通知を受け取るキュー
        self.que = que
        # 画面が閉じられた時のコールバック
        self.close_callback = close_callback

        context = Context(self.__class__.__name__)
        self.config = context.config
        self.setting = context.setting
        self.logger = context.logger

        config = self.setting.get(section="Settings", key="save_data_json_path")
        # ハンドラ初期化
        self.commander = Command()
        self.json_handler = JsonHandler(config.get(section="Settings", key="save_data_json_path"))
        self.device_handler = DeviceHandler()
        self.freq_device_handler = FreqDeviceHandler()

        # 画面をアクティブ
        self.dialog.focus_set()

        # メイン画面からの通知受信キューを設定
        self.set_queue()

    # 通知待ちキューをセット
    def set_queue(self):
        # 切断通知のレシーバーを別スレッドで待機
        thread = threading.Thread(target=self.notice_receiver, daemon=True)
        thread.start()

    # メインスレッドからの通知を待つ
    def notice_receiver(self):
        while True:
            message = self.que.get()
            self.context.logger.debug(message)
            if "disconnect" in message:
                # 画面を閉じる
                self.after(0, self.handle_close())
            elif "view top" in message:
                # 画面を最前面に表示
                self.after(0, self.dialog.lift())
                # 画面をアクティブ
                self.after(0, self.dialog.focus_set())

    def handle_close(self):
        if self.close_callback:
            self.close_callback(self.screen_id, self.que_key)
        self.dialog.destroy()

