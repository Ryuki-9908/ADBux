class AdbException(Exception):
    def __init__(self, arg=""):
        self.arg = arg


class NoDeviceSelect(AdbException):
    def __str__(self):
        return (
            f"対象のデバイスが選択されていません。"
        )
