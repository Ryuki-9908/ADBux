from db.sqlite_manager import SQLiteManager
from db.models.install_app_path_model import InstallAppPathModel


class InstallAppPathDao:
    def __init__(self):
        self.manager = SQLiteManager()
        self.table_name = InstallAppPathModel.__table_name__

    def insert(self, name, path):
        """アプリインストール画面の指定パスをINSERT"""
        query = f"""
            INSERT INTO {self.table_name} (name, path) VALUES (?, ?)
        """
        self.manager.execute_query(query, (name, path))

    def read(self, path_id=None):
        query = f"""
            SELECT * FROM {self.table_name}
        """
        conditions = []
        params = []

        if path_id:
            conditions.append("path_id = ?")
            params.append(path_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        return self.manager.execute_query(query, tuple(params))

    def get_all_path(self) -> dict:
        """保存してあるすべてのパスを取得"""
        query = f"""
            SELECT * FROM {self.table_name}
        """
        entity = self.manager.execute_query(query)
        path_list = {}
        for e in entity:
            path_list[e[0]] = e[1]
        return path_list

    def update(self, path_id, name, path):
        query = f"""
            UPDATE {self.table_name} SET name = ? path = ? 
            WHERE path_id = ?
        """
        self.manager.execute_update(query, (name, path, path_id))

    def delete(self, path_id):
        query = f"""
            DELETE FROM {self.table_name} WHERE path_id = ?
        """
        self.manager.execute_update(query, (path_id,))
