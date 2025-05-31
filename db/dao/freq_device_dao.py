from db.sqlite_manager import SQLiteManager
from db.models.freq_device_model import FreqDeviceModel


class FreqDeviceDao:
    def __init__(self):
        self.manager = SQLiteManager()
        self.table_name = FreqDeviceModel.__table_name__

    def insert(self, ipaddr, port=None):
        """よく使うデバイスをINSERT"""
        query = f"""
            INSERT INTO {self.table_name} VALUES (?, ?)
        """
        self.manager.execute_query(query, (ipaddr, port))

    def read(self, ipaddr=None, port=None):
        query = f"""
            SELECT * FROM {self.table_name}
        """
        conditions = []
        params = []

        if ipaddr:
            conditions.append("ipaddr = ?")
            params.append(ipaddr)
        if port:
            conditions.append("port = ?")
            params.append(port)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        return self.manager.execute_query(query, tuple(params))

    def update(self, ipaddr, port):
        query = f"""
            UPDATE {self.table_name} SET ipaddr = ?, port = ?
            WHERE ipaddr = ?
        """
        params = (ipaddr, port)
        self.manager.execute_update(query, params)

    def delete(self, ipaddr):
        query = f"""
            DELETE FROM {self.table_name} WHERE ipaddr = ?
        """
        self.manager.execute_update(query, (ipaddr,))

