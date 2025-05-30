import tkinter as tk
from tkinter import ttk, messagebox
from ui import screen_ids
from ui.base_dialog import BaseDialog
from utils import colors


class DeviceConnectDialog(BaseDialog):
	def __init__(self, dialog, que_key, que, close_callback):
		super().__init__(dialog, screen_ids.NETWORK_CONNECT_SCREEN, que_key, que, close_callback)
		""" 初期化処理 """
		# メイン画面からの通知受信キューを設定
		self.set_queue()
		# 保存されたよく使う端末を取得
		self.saved_devices = self.freq_device_handler.get_all_device()

		""" 画面表示 初期化 """
		self.connection_type = tk.IntVar()
		self.type_eth = tk.Radiobutton()
		self.type_wifi = tk.Radiobutton()
		self.ip_com = ttk.Combobox()
		self.port_filed = tk.Entry()

		# デバイス接続画面生成
		self.create_connect_view()

	# ネットワーク通信可能なデバイスを取得
	def get_devices(self, event=None):
		self.ip_com["values"] = tuple(self.saved_devices)

	def handle_close(self):
		if self.close_callback:
			self.close_callback(screen_ids.NETWORK_CONNECT_SCREEN, self.que_key)
		self.dialog.destroy()

	# adb connectを実行
	def adb_connect(self, event=None):
		ip_addr = self.ip_com.get()
		port = self.port_filed.get()
		try:
			result = self.device_handler.connect(ip_addr, port)
			if result == "connect":
				self.log.info("connect success.")
				messagebox.showinfo("成功", "【" + ip_addr + "】" + "に接続しました。", parent=self.dialog)
				self.handle_close()
			elif result == "already":
				self.log.info("already　connected.")
				messagebox.showinfo("メッセージ", "【" + ip_addr + "】" + "は既に接続されています。", parent=self.dialog)
				self.handle_close()
			else:
				self.log.error("connect failed.")
				messagebox.showerror("失敗", "接続に失敗しました。", parent=self.dialog)
		except Exception as e:
			self.log.error(e)
			messagebox.showerror("失敗", "接続に失敗しました。", parent=self.dialog)

	def create_connect_view(self):
		# 背景色
		background_color = colors.BACKGROUND_COLOR

		# GUI生成
		self.dialog.title("【ネットワーク接続】")
		self.dialog.geometry("300x130")
		self.dialog.resizable(width=False, height=False)
		self.dialog.configure(bg=background_color)

		# メインフレームの設定
		self.dialog.grid_rowconfigure(0, weight=3)
		self.dialog.grid_rowconfigure(1, weight=1)
		self.dialog.grid_rowconfigure(2, weight=1)
		self.dialog.grid_columnconfigure(0, weight=1)

		# ラジオボタン表示領域
		radio_bt_frame = tk.Frame(self.dialog)
		radio_bt_frame.grid(row=0, column=0, sticky="nsew")
		radio_bt_frame.configure(bg=background_color)

		self.connection_type.set(0)
		self.type_eth = tk.Radiobutton(radio_bt_frame, value=0, variable=self.connection_type, text="ETH", bg=background_color)
		self.type_eth.place(x=20, y=20)

		self.type_wifi = tk.Radiobutton(radio_bt_frame, value=1, variable=self.connection_type, text="Wi-Fi", bg=background_color)
		self.type_wifi.place(x=80, y=20)

		ip_port_frame = tk.Frame(self.dialog)
		ip_port_frame.grid(row=1, column=0, sticky="nsew")
		ip_port_frame.configure(bg=background_color)

		ip_port_frame.grid_columnconfigure(0, weight=3)
		ip_port_frame.grid_columnconfigure(1, weight=1)
		self.ip_com = ttk.Combobox(ip_port_frame, width=30, postcomman=self.get_devices)
		self.ip_com.bind("<<ComboboxSelected>>", self.get_devices)
		self.ip_com["values"] = ["―"]
		self.ip_com.grid(row=0, column=0, sticky="nsew", padx=5)

		self.port_filed = tk.Entry(ip_port_frame, width=10)
		self.port_filed.grid(row=0, column=1, sticky="nsew", padx=5)

		connect_bt = tk.Button(self.dialog, text="接続")
		connect_bt.bind("<Button-1>", self.adb_connect)
		connect_bt.grid(row=2, column=0, sticky="ew", padx=5)

		# サブウィンドウが閉じられるときの処理
		self.dialog.protocol("WM_DELETE_WINDOW", self.handle_close)
