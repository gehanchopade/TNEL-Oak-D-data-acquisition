import depthai as dai

def getMXID():
    if(len(dai.Device.getAllAvailableDevices())==1):
        print("Mx ID: "+dai.Device.getAllAvailableDevices()[0].getMxId())
    else:
        if(len(dai.Device.getAllAvailableDevices())==0):
            print("No Camera detected")
        else:
            print("Multiple cameras detected. Connect one camera")

if __name__=="__main__":
    getMXID()