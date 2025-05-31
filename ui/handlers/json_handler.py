import json


class JsonHandler:
    def __init__(self, json_file):
        super(JsonHandler, self).__init__()
        self.json_file = json_file
        self.save_data: dict = {}
        self.__load()

    def __load(self):
        try:
            with open(self.json_file, "r") as f:
                self.save_data = json.load(f)
        except FileNotFoundError:
            self.save_data = {}

    def save(self):
        with open(self.json_file, "w") as f:
            json.dump(self.save_data, f, indent=4)

    def get(self, key):
        self.__load()
        return self.save_data.get(key)

    def set(self, key, value):
        self.save_data[key] = value
        self.save()

    def delete(self, key, value):
        self.save_data[key].remove(value)
