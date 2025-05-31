from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class InstallAppPathModel:
    __table_name__ = "install_app_path"

    path_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(), nullable=False)
    path = Column(String(), nullable=False)

    def __repr__(self):
        return f"<InstallAppPath(path_id={self.path_id}, name={self.name}, path='{self.path}')>"
