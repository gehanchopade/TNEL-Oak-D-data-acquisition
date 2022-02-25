import json

class getConfigData():
    def __init__(self,path="../config.json"):
        self.path_to_config=path
        self.config=self.get_config()
    def get_config(self):
        with open(self.path_to_config,'rb') as file:
            config=json.load(file)
        return config
    def get_camera_config(self):
        return self.config['camera_config']
    def get_record_config(self):
        return self.config['record']
