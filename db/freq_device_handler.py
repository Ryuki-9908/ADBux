from db import sqlite_manager


class FreqDeviceHandler(sqlite_manager.SQLiteManager):
    table_name = "freq_devices"

    def insert(self, ipaddr):
        """よく使うデバイスをINSERT"""
        query = "INSERT INTO {} VALUES (?)".format(self.table_name)
        self.execute_query(query, (ipaddr,))

    def get_all_device(self):
        """全デバイスを取得"""
        query = "SELECT * FROM {}".format(self.table_name)
        devices = self.execute_query(query)
        ipaddr_list = []
        for device in devices:
            ipaddr_list.append(device[0])
        return ipaddr_list

    def update(self, ipaddr):
        query = "UPDATE {} SET ipaddr = ? WHERE ipaddr = ?".format(self.table_name)
        self.execute_update(query, (ipaddr,))

    def delete(self, ipaddr):
        query = "DELETE FROM {} WHERE ipaddr = ?".format(self.table_name)
        self.execute_update(query, (ipaddr,))
