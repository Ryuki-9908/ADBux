import sqlite3

from config.settings import Settings


class SQLiteManager:
    def __init__(self):
        # 設定ファイル読み込み
        config = Settings()
        db_path = config.get(section="Settings", key="db_path")
        self.db_path = db_path
        self.conn = None
        self.create()

    def connect(self):
        """データベース接続"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)

    def close(self):
        """データベース接続終了"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """クエリ実行"""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()
        return cursor.fetchall()

    def execute_update(self, query, params=None):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()

    def create(self):
        self.connect()
        with sqlite3.connect(self.db_path) as self.conn:
            try:
                cur = self.conn.cursor()
                # table生成
                cur.execute('CREATE TABLE freq_devices(ipaddr STRING PRIMARY KEY)')
                cur.execute('CREATE TABLE used_devices(id INTEGER PRIMARY KEY AUTOINCREMENT, ipaddr STRING, port STRING)')
                cur.execute('CREATE TABLE app_path(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, path STRING UNIQUE)')
                # DBコミット
                self.conn.commit()
            except Exception as e:
                print(e)
