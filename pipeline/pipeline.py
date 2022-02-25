import sys
sys.path.append('../')
from utils.getConfig import getConfigData
try:
    import depthai as dai
except:
    print("Run \"python3 install_requirements.py\" to install dependencies or follow README for setup instructions")
    sys.exit(42)

class Pipeline():
    def __init__(self):
        self.config=getConfigData().get_config()
        print(self.config)

if __name__=="__main__":
    pipeline=Pipeline()