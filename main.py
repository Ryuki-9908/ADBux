from ui import MainLayout
from download_scrcpy import DownloadScrcpy


if __name__ == "__main__":
    # scrcpyダウンロード
    DownloadScrcpy().download()

    # メイン処理開始
    app = MainLayout()
    app.mainloop()
