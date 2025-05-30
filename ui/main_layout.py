import queue
import threading
import tkinter as tk
from tkinter import Listbox, messagebox
import time
from exceptions.adb_exception import NoDeviceSelect
from ui import screen_ids
from ui.menu.connect_device_listbox_menu import ConnectDeviceListboxMenu
from utils import colors
from utils.log import Log
from utils.command import Command
from config.settings import Settings
from ui.menu.freq_used_listbox_menu import FreqUsedListboxMenu
from utils.device_handler import DeviceHandler
from db import freq_device_handler


class MainLayout(tk.Tk):
	def __init__(self):
		super().__init__()
		""" 初期化処理 """
		class_name = self.__class__.__name__
		# 各画面への通知用キューを画面IDに紐づけて生成
		self.queues = {}
		# ロガー生成
		self.log = Log(tag=class_name).get_logger()
		# 設定ファイル読み込み
		config = Settings()
		# ハンドラ初期化
		self.commander = Command()
		self.device_handler = DeviceHandler()
		self.freq_device_handler = freq_device_handler.FreqDeviceHandler()
		# 接続されたデバイスのリスト
		self.device_to_state = self.device_handler.get_connect_device()
		# タイマー初期化
		self.buftime = time.time()
		# 切断されたデバイス
		self.disconnect_devices = set()

		""" GUI生成 """
		self.title("Android制御ソフト")
		self.geometry("800x500")
		self.resizable(width=False, height=False)

		""" ウィジットの初期化 """
		# 接続されたデバイスリスト
		self.connect_device_list_view: tk.Listbox = Listbox()
		self.connect_device_menu: tk.Menu = tk.Menu()
		# よく使うデバイスリスト
		self.freq_used_device_list_view: tk.Listbox = Listbox()
		self.freq_used_device_menu: tk.Menu = tk.Menu()
		self.freq_menu = None

		""" メイン画面生成 """
		self.create_main()

		""" 監視サービス起動 """
		self.reload()
		self.time_event()

	def create_queues_key(self, screen_id, device):
		# 画面IDとIPアドレスを組み合わせたものをキーとして管理
		return f"{screen_id}_{device}"

	# 画面IDとデバイスIPをkeyに通知用キューを生成
	def add_queues(self, screen_id, device):
		is_new = False
		key = self.create_queues_key(screen_id, device)
		if key not in self.queues.keys():
			# ハッシュ値をKeyに通知用キューを追加
			self.queues[key] = queue.Queue()
			is_new = True
		que = self.queues[key]

		return is_new, que

	# 各画面へのデバイス切断通知
	def notice_queues(self):
		# 切断されたデバイスの取得は別スレッドのためローカル変数にコピーして扱う
		disconnect_devices = self.disconnect_devices.copy()
		self.disconnect_devices.clear()

		self.log.debug("notice queues call.")
		try:
			destroy_items = []
			# 何かしらの操作画面を表示しているデバイスリスト
			close_screen_list = self.queues.keys()
			for device in disconnect_devices:
				for item in close_screen_list:
					if device in item: destroy_items.append(item)

			# 切断されたデバイス操作画面に切断通知を送信
			for item in destroy_items:
				que = self.queues.get(item)
				device = item.split("_")[1]
				self.log.debug("[send] {} disconnected.".format(device))
				que.put("[receive] {} disconnected.".format(device))
		except Exception as e:
			self.log.error(e)

	# 毎秒、接続デバイスを自動更新
	def time_event(self):
		tmp = time.time()
		if(tmp - self.buftime) >= 0.5:
			# 非同期で監視で自動更新
			th = threading.Thread(target=self.reload)
			th.start()
			self.buftime = tmp
		self.after(1, self.time_event)

	# 接続されたデバイスのリストを更新
	def reload(self, event=None):
		show_devices = []
		tmp = self.device_to_state.copy()
		self.device_to_state.clear()
		self.device_to_state = self.device_handler.get_connect_device()
		for device in self.device_to_state.keys():
			if self.device_to_state[device] == "offline":
				device = str(device + "(" + self.device_to_state[device] + ")")
			show_devices.append(device)
		if self.device_to_state != tmp:
			self.connect_device_list_view.delete(0, tk.END)
			self.connect_device_list_view.insert(tk.END, *show_devices)

		# 接続中デバイス数が減った場合はデバイスが切断されたと判断
		if len(tmp) > len(self.device_to_state):
			# 各画面に切断通知
			self.disconnect_devices = set(self.device_to_state.keys()) ^ set(tmp.keys())
			th = threading.Thread(target=self.notice_queues)
			th.start()

		if (event is not None) and (self.freq_menu is not None):
			self.log.debug("device list reload button click.")
			save_data = self.freq_device_handler.get_all_device()
			self.freq_menu.show_list_reload(save_data)

	# 選択したデバイスを切断
	def disconnect(self, event=None):
		# 結果用
		result = False
		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			if device is None:
				# デバイスが接続されていない場合
				messagebox.showerror("Error", "デバイスが接続されていません。", parent=self)
			else:
				execution = messagebox.askokcancel("確認", "【" + device + "】" + "を切断します。よろしいですか？", parent=self)
				if execution:
					# 切断処理
					result = self.device_handler.disconnect(tar_device=device)
					if result:
						self.log.info("connect success.")
						messagebox.showinfo("Success", "【" + device + "】" + "を切断しました。", parent=self)
					else:
						self.log.error("disconnected failed.")
						messagebox.showerror("Error", "【" + device + "】" + "の切断に失敗しました。", parent=self)
		except NoDeviceSelect as e:
			self.log.error(e)
			messagebox.showerror("Error", "対象のデバイスを選択してください。", parent=self)
		except Exception as e:
			self.log.error(e)

	# scrcpyで画面表示
	def show_screen(self, event=None):
		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			if device is None:
				# デバイスが接続されていない場合
				messagebox.showerror("Error", "デバイスが接続されていません。", parent=self)
			else:
				ret = messagebox.askokcancel("確認", "【" + device + "】" + "の画面を表示します。よろしいですか？", parent=self)
				if ret:
					# 別スレッドで画面表示を実行
					thread = threading.Thread(target=self.device_handler.view_screen, args=(device,), daemon=True)
					thread.start()
		except Exception as e:
			self.log.error(e)
			messagebox.showerror("Error", "対象のデバイスを選択してください。", parent=self)

	""" 再起動 """
	def reboot(self, event=None):
		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			if device is None:
				# デバイスが接続されていない場合
				messagebox.showerror("Error", "デバイスが接続されていません。", parent=self)
			else:
				ret = messagebox.askokcancel("確認", "【" + device + "】" + "を再起動します。よろしいですか？", parent=self)
				if ret:
					# 再起動実行
					self.device_handler.reboot(device)
					messagebox.showinfo("Success", "【" + device + "】" + "に再起動処理を要求しました。", parent=self)
		except NoDeviceSelect as e:
			self.log.error(e)
			messagebox.showerror("Error", "対象のデバイスを選択してください。", parent=self)
		except Exception as e:
			self.log.error(e)

	""" シャットダウン """
	def shutdown(self, event=None):
		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			if device is None:
				# デバイスが接続されていない場合
				messagebox.showerror("Error", "デバイスが接続されていません。", parent=self)
			else:
				ret = messagebox.askokcancel("確認", "【" + device + "】" + "をシャットダウンします。よろしいですか？", parent=self)
				if ret:
					# シャットダウン実行
					self.device_handler.shutdown(device)
					messagebox.showinfo("Success", "【" + device + "】" + "にシャットダウン処理を要求しました。", parent=self)
		except NoDeviceSelect as e:
			self.log.error(e)
			messagebox.showerror("Error", "対象のデバイスを選択してください。", parent=self)
		except Exception as e:
			self.log.error(e)

	""" TimeZone設定 """
	def timezone_setting(self, event=None):
		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			if device is None:
				# デバイスが接続されていない場合
				messagebox.showerror("Error", "デバイスが接続されていません。", parent=self)
			else:
				# TimeZoneを東京に設定
				if self.device_handler.timezone_setting(device):
					messagebox.showinfo("Success", "【" + device + "】" + "のタイムゾーン設定を東京に変更しました。", parent=self)
				else:
					messagebox.showerror("Error", "【" + device + "】" + "のタイムゾーン設定に失敗しました。", parent=self)
		except NoDeviceSelect as e:
			self.log.error(e)
			messagebox.showerror("Error", "対象のデバイスを選択してください。", parent=self)
		except Exception as e:
			self.log.error(e)

	""" 端末の画面撮影 """
	def screen_shot(self, event):
		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			if device is None:
				# デバイスが接続されていない場合
				messagebox.showerror("失敗", "デバイスが接続されていません。", parent=self)
			else:
				# アプリの再起動実行
				self.device_handler.screen_shot(device)
				messagebox.showinfo("成功", "【" + device + "】" + "の画面キャプチャを取得しました。", parent=self)
		except NoDeviceSelect as e:
			self.log.error(e)
			messagebox.showerror("失敗", "対象のデバイスを選択してください。", parent=self)
		except Exception as e:
			self.log.error(e)
			messagebox.showerror("失敗", "画面キャプチャ取得の要求に失敗しました。", parent=self)

	""" アプリインストール画面表示 """
	def show_install_window(self, event):
		def show_task(select_device):
			from ui import ApplicationInstallDialog
			""" 選択したデバイスが切断されたことを通知するキューを生成 """
			is_new, que = self.add_queues(screen_ids.APPLICATION_INSTALL_SCREEN, select_device)
			if is_new:
				dialog = tk.Toplevel(self)
				ApplicationInstallDialog(dialog, select_device, que, close_callback=self.close_callback)
			else:
				# 既に開かれている場合は画面をトップに移動
				que.put("view top.")

		try:
			# 対象デバイスが接続されているかの確認
			idx = self.connect_device_list_view.curselection()[0]
			tar_device = self.connect_device_list_view.get(first=idx, last=idx)[0]
			device = self.device_handler.check_execution(tar_device=tar_device)
			# 非同期で画面表示
			th = threading.Thread(target=show_task(device))
			th.start()
		except NoDeviceSelect as e:
			self.log.error(e)
			messagebox.showerror("失敗", "対象のデバイスを選択してください。", parent=self)
		except Exception as e:
			self.log.error(e)
			messagebox.showerror("失敗", "対象のデバイスが見つかりません。", parent=self)

	""" デバイス接続画面表示 """
	def show_connect_window(self, event):
		def show_task():
			from ui import DeviceConnectDialog
			# 対象デバイスは存在しないため固定値をキーとする。
			que_key = "0000"
			is_new, que = self.add_queues(screen_ids.NETWORK_CONNECT_SCREEN, que_key)
			if is_new:
				dialog = tk.Toplevel(self)
				DeviceConnectDialog(dialog, que_key, que, close_callback=self.close_callback)
			else:
				# 既に開かれている場合は画面をトップに移動
				que.put("view top.")

		try:
			# 非同期で画面表示
			th = threading.Thread(target=show_task())
			th.start()
		except Exception as e:
			self.log.error(e)

	""" サブ画面が閉じられた時のコールバック """
	def close_callback(self, screen_id, device,):
		key = self.create_queues_key(screen_id, device)
		# キューを削除
		self.queues.pop(key)

	""" メイン画面表示 """
	def create_main(self):
		# 背景色
		background_color = colors.BACKGROUND_COLOR
		
		# 背景色を設定
		self.configure(bg=background_color)
		
		connect_devices_label = tk.Label(text="接続されているデバイス一覧", bg=background_color)
		connect_devices_label.place(x=20, y=20)

		reload_bt = tk.Button(self, text="手動更新")
		reload_bt.bind("<Button-1>", self.reload)
		reload_bt.place(x=200, y=18)

		disconnect_bt = tk.Button(self, text="切断")
		disconnect_bt.bind("<Button-1>", self.disconnect)
		disconnect_bt.place(x=280, y=18)

		""" 接続されたデバイス """
		connect_device = [device for device in self.device_to_state.keys()]
		connect_device_items = tk.StringVar(self, value=connect_device)
		self.connect_device_list_view = Listbox(self, listvariable=connect_device_items, height=11, width=50)
		self.connect_device_list_view.place(x=15, y=50)

		""" よく使うデバイス """
		freq_used_device_label = tk.Label(self, text="よく使うデバイス", bg=background_color)
		freq_used_device_label.place(x=20, y=250)

		save_data = self.freq_device_handler.get_all_device()
		freq_used_device_items = tk.StringVar(value=save_data)
		self.freq_used_device_list_view = Listbox(self, listvariable=freq_used_device_items, height=12, width=50)
		self.freq_used_device_list_view.place(x=15, y=280)

		""" ListBoxにメニュー操作をバインド """
		# よく使うデバイス
		self.freq_menu = FreqUsedListboxMenu(self, self.freq_used_device_list_view, device_handler=self.device_handler)
		self.freq_used_device_list_view.bind("<Button-3>", self.freq_menu.show_menu)

		# 接続されたデバイス
		connected_menu = ConnectDeviceListboxMenu(self, self.connect_device_list_view, freq_used_listbox=self.freq_used_device_list_view, device_handler=self.device_handler)
		self.connect_device_list_view.bind("<Button-3>", connected_menu.show_menu)

		""" 端末操作画面 """
		operation_label = tk.Label(self, text="----- 端末操作 -----", bg=background_color)
		operation_label.place(x=370, y=20)

		install_bt = tk.Button(self, text="アプリインストール")
		install_bt.bind("<Button-1>", self.show_install_window)
		install_bt.place(x=380, y=50, width=100)

		screen_bt = tk.Button(self, text="端末画面表示")
		screen_bt.bind("<Button-1>", self.show_screen)
		screen_bt.place(x=510, y=50, width=100)

		connect_label = tk.Label(self, text="----- 接続 -----", bg=background_color)
		connect_label.place(x=370, y=100)

		connect_bt = tk.Button(self, text="端末接続")
		connect_bt.bind("<Button-1>", self.show_connect_window)
		connect_bt.place(x=380, y=130, width=100)

		power_label = tk.Label(self, text="----- 電源 -----", bg=background_color)
		power_label.place(x=370, y=180)

		reboot_bt = tk.Button(self, text="端末再起動")
		reboot_bt.bind("<Button-1>", self.reboot)
		reboot_bt.place(x=380, y=210, width=100)

		shutdown_bt = tk.Button(self, text="端末シャットダウン")
		shutdown_bt.bind("<Button-1>", self.shutdown)
		shutdown_bt.place(x=510, y=210, width=100)

		info_label = tk.Label(self, text="----- 情報取得 -----", bg=background_color)
		info_label.place(x=370, y=260)

		no_code = tk.Button(self, text="未実装")
		no_code.bind("<Button-1>")
		no_code.place(x=380, y=290, width=100)

		other_label = tk.Label(self, text="----- その他 -----", bg=background_color)
		other_label.place(x=370, y=340)

		timezone_bt = tk.Button(self, text="TimeZone設定")
		timezone_bt.bind("<Button-1>", self.timezone_setting)
		timezone_bt.place(x=380, y=370, width=100)

		screen_shot_bt = tk.Button(self, text="画面キャプチャ取得")
		screen_shot_bt.bind("<Button-1>", self.screen_shot)
		screen_shot_bt.place(x=510, y=370, width=100)
