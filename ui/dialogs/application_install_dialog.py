import datetime
import glob
import os
import threading
import tkinter as tk
from tkinter import Listbox, filedialog, messagebox
from ui import screen_ids
from ui.dialogs.base_dialog import BaseDialog
from utils import colors


class ApplicationInstallDialog(BaseDialog):
    def __init__(self, dialog, device, que, close_callback):
        super().__init__(dialog, screen_ids.APPLICATION_INSTALL_SCREEN, device, que, close_callback)
        """ 初期化処理 """
        # デフォルトの参照フォルダパスを取得
        self.default_path = self.json_handler.get("last_path")
        # 対象のデバイス
        self.device = device
        # インストール可能なアプリのリスト
        self.app = []
        self.select = []

        # メイン画面からの通知受信キューを設定
        self.set_queue()

        """ 画面表示 初期化 """
        self.folder_path = tk.StringVar()
        self.app_list = Listbox()
        self.select_list = Listbox()

        # アプリケーションインストール画面生成
        self.create_app_install_view()

    # フォルダ選択ダイアログ
    def select_folder(self):
        folder_path = filedialog.askdirectory(parent=self.dialog, title="フォルダを選択", initialdir=self.default_path)
        if folder_path:  # フォルダが選択された場合
            self.folder_path.set(folder_path)
            self.reload()

    # アプリのリストを更新
    def reload(self, event=None):
        # 初期化
        self.app = []
        self.select = []
        # ファイル名を取得
        files = glob.glob(self.folder_path.get() + "\\*.apk")
        for file in files:
            self.app.append(file)
        # アプリ一覧を更新
        self.app_list.delete(0, tk.END)
        self.show_app_name(self.app_list, self.app)
        # 選択中リストをクリア
        self.select_list.delete(0, tk.END)

    def show_app_name(self, listbox: Listbox, app_list: list):
        apk_list = []
        for path in app_list:
            timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            show_name = f"{os.path.basename(path)} ({timestamp})"
            listbox.insert(tk.END, show_name)
        return apk_list

    # インストールするアプリを選択リストに追加
    def add_app(self, event):
        select_app = []
        idx = self.app_list.curselection()
        self.select.append(self.app[idx[0]])
        select_app.append(self.app[idx[0]])
        self.show_app_name(self.select_list, select_app)
        self.app_list.delete(idx[0])
        del self.app[idx[0]]

    # 選択リストからアプリを削除
    def delete_app(self, event):
        del_app = []
        idx = self.select_list.curselection()
        self.app.append(self.select[idx[0]])
        del_app.append(self.select[idx[0]])
        self.show_app_name(self.app_list, del_app)
        self.select_list.delete(idx[0])
        del self.select[idx[0]]

    # アプリ一覧から全てを選択リストに追加
    def all_add_app(self, event):
        self.select = self.select + self.app
        select_app = self.app.copy()
        self.show_app_name(self.select_list, select_app)
        self.app_list.delete(0, tk.END)
        self.app.clear()

    # 選択リストから全てのアプリを削除
    def all_del_app(self, event):
        del_app = []
        self.app = self.app + self.select
        del_app = self.select.copy()
        self.show_app_name(self.app_list, del_app)
        self.select_list.delete(0, tk.END)
        self.select.clear()

    # アプリをインストール
    def adb_install(self, event):
        def install():
            failure = []
            ret = messagebox.askyesno("アプリインストール確認", str(len(self.select)) + "個のアプリを【" + self.device + "】にインストールします。よろしいでしょうか？", parent=self.dialog)
            if ret:
                for app in self.select:
                    result = self.commander.send_command(['adb', '-s', self.device, 'install', '-r', '-t', app], timeout=None)
                    if not result:
                        failure.append(app[6:])
                        continue
                    result = result.stdout.splitlines()
                    if len(result) == 2 and result[1] != "Success":
                        failure.append(app[6:])
                # インストール要求が完了したら画面を前面固定にして表示
                self.dialog.attributes('-topmost', True)
                if len(failure) == 0:
                    messagebox.showinfo("Success", str(len(self.select)) + "個のインストールに成功しました。", parent=self.dialog)
                else:
                    messagebox.showerror("Error",
                                         str(len(failure)) + "個のインストールに失敗しました。", parent=self.dialog)
                # 前面固定を解除
                self.dialog.attributes('-topmost', False)
        # インストールは非同期で行う
        thread = threading.Thread(target=install, daemon=True)
        thread.start()

    def save_last_path(self):
        """現在のパスを設定ファイルに保存する"""
        self.json_handler.set(key="last_path", value=self.folder_path.get())

    def handle_close(self):
        if self.close_callback:
            self.close_callback(screen_ids.APPLICATION_INSTALL_SCREEN, self.device)
        self.save_last_path()
        self.dialog.destroy()

    def create_app_install_view(self):
        # 背景色
        background_color = colors.BACKGROUND_COLOR

        # GUI生成
        self.dialog.title("【アプリインストール】" + self.device)
        self.dialog.geometry("600x400")
        self.dialog.resizable(width=False, height=False)
        self.dialog.configure(bg=background_color)

        # メインフレームの設定
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=9)
        self.dialog.grid_columnconfigure(0, weight=1)

        # フォルダ選択フレームの設定
        folder_frame = tk.Frame(self.dialog)
        folder_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
        folder_frame.configure(bg=background_color)
        # 二列に分割
        folder_frame.grid_columnconfigure(0, weight=1)  # Entryをリサイズ可能にする
        folder_frame.grid_columnconfigure(1, weight=0)  # ボタンは固定サイズ

        # Entry（フォルダパスを表示）
        self.folder_path = tk.StringVar(value=self.default_path)
        entry = tk.Entry(folder_frame, textvariable=self.folder_path, font=("Arial", 10))
        entry.grid(row=0, column=0, sticky="nsew", padx=5)

        # 参照ボタン
        button = tk.Button(folder_frame, text="参照", command=self.select_folder, font=("Arial", 10))
        button.grid(row=0, column=1, sticky="e", padx=5)

        # アプリ選択フレームの設定
        app_frame = tk.Frame(self.dialog)
        app_frame.grid(row=1, column=0, sticky="nsew")
        app_frame.configure(bg=background_color)

        app_frame.grid_rowconfigure(0, weight=1)
        app_frame.grid_rowconfigure(1, weight=1)
        app_frame.grid_rowconfigure(2, weight=1)
        app_frame.grid_rowconfigure(3, weight=1)
        app_frame.grid_rowconfigure(4, weight=1)
        app_frame.grid_columnconfigure(0, weight=1)

        app_label = tk.Label(app_frame, text="アプリ一覧", bg=background_color)
        app_label.grid(row=0, column=0, sticky="w", padx=15)

        reload_bt = tk.Button(app_frame, text="一覧更新")
        reload_bt.bind("<Button-1>", self.reload)
        reload_bt.grid(row=0, column=0, sticky="e", padx=15)

        app_item = tk.StringVar(value=self.app)
        self.app_list = Listbox(app_frame, listvariable=app_item, height=7)
        self.app_list.grid(row=1, column=0, sticky="ew", padx=15)

        padding_x = 15
        select_label = tk.Label(app_frame, text="選択中", bg=background_color)
        select_label.grid(row=2, column=0, sticky="w", padx=padding_x)

        padding_x += 65
        select_bt = tk.Button(app_frame, text="▼ 追加")
        select_bt.bind("<Button-1>", self.add_app)
        select_bt.grid(row=2, column=0, sticky="w", padx=padding_x)

        padding_x += 65
        delete_bt = tk.Button(app_frame, text="▲ 解除")
        delete_bt.bind("<Button-1>", self.delete_app)
        delete_bt.grid(row=2, column=0, sticky="w", padx=padding_x)

        padding_x = 15
        all_sec_bt = tk.Button(app_frame, text=" クリア ", width=10)
        all_sec_bt.bind("<Button-1>", self.all_del_app)
        all_sec_bt.grid(row=2, column=0, sticky="e", padx=padding_x)

        padding_x += 90
        all_sec_bt = tk.Button(app_frame, text="一括選択", width=10)
        all_sec_bt.bind("<Button-1>", self.all_add_app)
        all_sec_bt.grid(row=2, column=0, sticky="e", padx=padding_x)

        select_item = tk.StringVar(value=self.select)
        self.select_list = Listbox(app_frame, listvariable=select_item, height=7)
        self.select_list.grid(row=3, column=0, sticky="ew", padx=15)

        install_bt = tk.Button(app_frame, text="インストール", width=20)
        install_bt.bind("<Button-1>", self.adb_install)
        install_bt.grid(row=4, column=0, sticky="e", padx=15)

        self.reload()

        # サブウィンドウが閉じられるときの処理
        self.dialog.protocol("WM_DELETE_WINDOW", self.handle_close)

