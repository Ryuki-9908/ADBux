from ui import MainWindow
from download_scrcpy import DownloadScrcpy


if __name__ == "__main__":
    # scrcpyダウンロード
    DownloadScrcpy().download()

    # メイン処理開始
    app = MainWindow()
    app.mainloop()
