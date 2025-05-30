from db import sqlite_manager


class InstallAppPathHandler(sqlite_manager.SQLiteManager):
    table_name = "install_app_path"

    def insert(self, name, path):
        """アプリインストール画面の指定パスをINSERT"""
        query = "INSERT INTO {} (name, path) VALUES (?, ?)".format(self.table_name)
        self.execute_query(query, (name, path))

    def get_all_path(self) -> dict:
        """保存してあるすべてのパスを取得"""
        query = "SELECT * FROM {}".format(self.table_name)
        entity = self.execute_query(query)
        path_list = {}
        for e in entity:
            path_list[e[0]] = e[1]
        return path_list

    def update(self, name, path):
        query = "UPDATE {} SET name = ? WHERE name = ?".format(self.table_name)
        self.execute_update(query, (name, path))

    def delete(self, name, path):
        query = "DELETE FROM {} WHERE ipaddr = ?".format(self.table_name)
        self.execute_update(query, (ipaddr,))
