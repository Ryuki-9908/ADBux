from db import sqlite_manager


class UsedDevices(sqlite_manager.SQLiteManager):
    table_name = "used_devices"

    def insert(self, ipaddr, port):
        """使用したデバイスをINSERT"""
        query = "INSERT INTO {} (ipaddr, port) VALUES (?, ?)".format(self.table_name)
        self.execute_query(query, (ipaddr, port))

    def get_all_device(self):
        """デバイスを取得"""
        query = "SELECT * FROM {}".format(self.table_name)
        return self.execute_query(query)
