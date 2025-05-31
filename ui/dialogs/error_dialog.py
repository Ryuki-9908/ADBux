from tkinter import messagebox

error_show = False


class ErrorDialog:
	def show_error(self, error_message):
		global error_show
		"""エラーメッセージを表示するメソッド。重複して表示しない。"""
		if not error_show:
			messagebox.showerror("Error", error_message, parent=self)
			error_show = True
		else:
			error_show = False
			self.show_error(error_message)
