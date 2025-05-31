import sqlite3
from core.context import Context


class SQLiteManager(Context):
    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.db_path = self.config.DB_PATH
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
                cur.execute('CREATE TABLE freq_devices(ipaddr STRING PRIMARY KEY, port STRING)')
                cur.execute('CREATE TABLE used_devices(id INTEGER PRIMARY KEY AUTOINCREMENT, ipaddr STRING, port STRING)')
                cur.execute('CREATE TABLE app_path(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, path STRING UNIQUE)')
                # DBコミット
                self.conn.commit()
            except Exception as e:
                print(e)
