from db.dao.install_app_path_dao import InstallAppPathDao


class InstallAppPathHandler(InstallAppPathDao):
    def get_all_path(self) -> dict:
        """保存してあるすべてのパスを取得"""
        entity = self.read()
        path_list = {}
        for e in entity:
            path_list[e[0]] = e[1]
        return path_list
