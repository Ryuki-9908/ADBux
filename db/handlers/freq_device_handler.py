from db.dao.freq_device_dao import FreqDeviceDao


class FreqDeviceHandler(FreqDeviceDao):
    def get_all_device(self):
        """全デバイスを取得"""
        devices = self.read()
        ipaddr_list = []
        for device in devices:
            ipaddr_list.append(device[0])
        return ipaddr_list

