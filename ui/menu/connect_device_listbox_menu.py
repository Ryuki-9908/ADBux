import tkinter as tk
from tkinter import messagebox

from exceptions.adb_exception import NoDeviceSelect
from ui.handlers.device_handler import DeviceHandler
from core.logger import Logger
from ui.menu.freq_used_listbox_menu import freq_used_device_reload
from db.handlers import freq_device_handler


class ConnectDeviceListboxMenu:
    def __init__(self, master, listbox, freq_used_listbox, device_handler: DeviceHandler):
        class_name = self.__class__.__name__
        self.master = master
        self.listbox = listbox
        self.freq_used_listbox = freq_used_listbox
        # ロガー生成
        self.log = Logger(tag=class_name).get_logger()
        self.freq_device_handler = freq_device_handler.FreqDeviceHandler()
        self.device_handler = device_handler

    def show_menu(self, event):
        index = self.listbox.nearest(event.y)
        self.listbox.select_set(index)

        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="よく使うデバイスに追加", command=lambda: self.device_save())
        menu.add_command(label="切断", command=lambda: self.adb_disconnect())
        menu.post(event.x_root, event.y_root)

    def device_save(self):
        try:
            # お気に入りデバイスリストが保存されたjson
            save_data = self.freq_device_handler.get_all_device()
            # 選択されたデバイスを取得
            device = self.listbox.get(self.listbox.curselection(), self.listbox.curselection())[0]
            if len(device) == 0:
                messagebox.showerror("エラー", "登録するデバイスを選択してください。", parent=self.master)
                return
            elif device not in save_data:
                self.freq_device_handler.insert(device)
                messagebox.showinfo("Success", "【" + device + "】" + "をよく使うデバイスに登録しました。", parent=self.master)
                # よく使うデバイスリストを更新
                freq_used_device_reload(self.freq_used_listbox, self.freq_device_handler.get_all_device())
            else:
                messagebox.showinfo("Info", "【" + device + "】" + "は既に追加されています。", parent=self.master)
        except Exception as e:
            self.log.error(e)

    def adb_disconnect(self):
        # 結果用
        result = False
        try:
            # 対象デバイスが接続されているかの確認
            device = self.listbox.get(self.listbox.curselection(), self.listbox.curselection())[0]
            device = self.device_handler.check_execution(tar_device=device, select_only=True)
            if not device:
                # デバイスが接続されていない場合
                messagebox.showerror("失敗", "デバイスが接続されていません。", parent=self.master)
            else:
                execution = messagebox.askokcancel("確認", "【" + device + "】" + "を切断します。よろしいですか？", parent=self.master)
                if execution:
                    # 切断処理
                    result = self.device_handler.disconnect(tar_device=device)

                if result:
                    self.log.info("disconnected success.")
                    messagebox.showinfo("成功", "【" + device + "】" + "を切断しました。", parent=self.master)
                else:
                    self.log.error("disconnected failed.")
                    messagebox.showerror("失敗", "【" + device + "】" + "の切断に失敗しました。", parent=self.master)
        except NoDeviceSelect as e:
            self.log.error(e)
            messagebox.showerror("失敗", "対象のデバイスを選択してください。", parent=self.master)
        except Exception as e:
            self.log.error(e)
