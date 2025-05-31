import tkinter as tk
from tkinter import messagebox

from ui.handlers.device_handler import DeviceHandler
from core.logger import Logger
from db.handlers import freq_device_handler


class FreqUsedListboxMenu:
    def __init__(self, master, listbox, device_handler: DeviceHandler):
        class_name = self.__class__.__name__
        self.master = master
        self.listbox = listbox
        self.device_handler = device_handler
        self.db_handler = freq_device_handler.FreqDeviceHandler()
        # ロガー生成
        self.log = Logger(tag=class_name).get_logger()

    def show_menu(self, event):
        index = self.listbox.nearest(event.y)
        self.listbox.select_set(index)

        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="リストから削除", command=lambda: self.device_delete())
        menu.add_command(label="ネットワーク接続", command=lambda: self.adb_connect())
        menu.post(event.x_root, event.y_root)

    def device_delete(self):
        try:
            save_data = self.db_handler.get_all_device()
            device = self.listbox.get(self.listbox.curselection(), self.listbox.curselection())[0]
            if len(device) == 0:
                messagebox.showerror("失敗", "削除するデバイスを選択してください。", parent=self.master)
                return
            elif device in save_data:
                # 新しいデバイスを削除
                self.db_handler.delete(ipaddr=device)
                messagebox.showinfo("成功", "【" + device + "】" + "をよく使うデバイスから削除しました。", parent=self.master)
                # リストを更新
                self.show_list_reload(self.db_handler.get_all_device())
            else:
                messagebox.showinfo("メッセージ", "【" + device + "】" + "は登録されていません。", parent=self.master)
        except Exception as e:
            self.log.error(e)

    def adb_connect(self):
        try:
            device = self.listbox.get(self.listbox.curselection(), self.listbox.curselection())[0]
            result = self.device_handler.connect(device)
            if result == "connect":
                self.log.info("connect success.")
                messagebox.showinfo("成功", "【" + device + "】" + "に接続しました。", parent=self.master)
            elif result == "already":
                self.log.info("already　connected.")
                messagebox.showinfo("メッセージ", "【" + device + "】" + "は既に接続されています。", parent=self.master)
            else:
                self.log.error("connect failed.")
                messagebox.showerror("失敗", "接続に失敗しました。", parent=self.master)
        except Exception as e:
            self.log.error(e)

    def show_list_reload(self, show_devices):
        freq_used_device_reload(self.listbox, show_devices)


# よく使うデバイスリストを更新
def freq_used_device_reload(listbox, show_devices):
    listbox.delete(0, tk.END)
    listbox.insert(tk.END, *show_devices)
