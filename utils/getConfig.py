import json

class getConfigData():
    def __init__(self,path="../config.json"):
        self.path_to_config=path
        self.config={}
    def get_config(self):
        with open(self.path_to_config,'rb') as file:
            self.config=json.load(file)
            print(self.config)
