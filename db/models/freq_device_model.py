from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FreqDeviceModel:
    __table_name__ = "freq_devices"

    ipaddr = Column(String(15), primary_key=True, nullable=False)
    port = Column(String(5), nullable=False)

    def __repr__(self):
        return f"<FreqDevices(ipaddr={self.ipaddr}, port='{self.port}')>"
