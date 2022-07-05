from utils.getConfig import getConfigData
import ray
from pipeline.pipeline import Pipeline
import os
import time
import sys

try:
    import depthai as dai
except:
    print("Run \"python3 install_requirements.py\" to install dependencies or follow README for setup instructions")
    sys.exit(42)

try:
    import depthai as dai
except:
    print("Run \"python3 install_requirements.py\" to install dependencies or follow README for setup instructions")
    sys.exit(42)


def getPipeLine(streamName):
    pipeline = dai.Pipeline()

    # Define sources and outputs
    # camRgb = pipeline.create(dai.node.ColorCamera)
    monoLeft = pipeline.create(dai.node.MonoCamera)
    monoRight = pipeline.create(dai.node.MonoCamera)
    # ve1 = pipeline.create(dai.node.VideoEncoder)
    ve2 = pipeline.create(dai.node.VideoEncoder)
    ve3 = pipeline.create(dai.node.VideoEncoder)

    # ve1Out = pipeline.create(dai.node.XLinkOut)
    ve2Out = pipeline.create(dai.node.XLinkOut)
    ve3Out = pipeline.create(dai.node.XLinkOut)

    # ve1Out.setStreamName(streamName[0])
    ve2Out.setStreamName(streamName[1])
    ve3Out.setStreamName(streamName[2])

    # Properties
    # camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    # Create encoders, one for each camera, consuming the frames and encoding them using H.264 / H.265 encoding
    # ve1.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_HIGH)
    ve2.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_HIGH)
    ve3.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_HIGH)

    # Linking
    monoLeft.out.link(ve2.input)
    # camRgb.video.link(ve1.input)
    monoRight.out.link(ve3.input)
    # ve1.bitstream.link(ve1Out.input)
    ve2.bitstream.link(ve2Out.input)
    ve3.bitstream.link(ve3Out.input)
    return pipeline

@ray.remote
def recordCam(mxID,path,streamName,camName,time_limit):
    pipeline=getPipeLine(streamName)
    isDev1,deviceInfo=dai.Device.getDeviceByMxId(mxID)
    with dai.Device(pipeline,deviceInfo) as dev:

        # Output queues will be used to get the encoded data from the outputs defined above
        outQ1 = dev.getOutputQueue(name=streamName[1], maxSize=30, blocking=False)
        # outQ2 = dev.getOutputQueue(name=streamName[1], maxSize=30, blocking=False)
        outQ3 = dev.getOutputQueue(name=streamName[2], maxSize=30, blocking=False)
        os.mkdir(path+'/'+camName)
        os.mkdir(path+'/'+camName+'/videos/')
        os.mkdir(path+'/'+camName+'/frames/')
        name=path+'/'+camName+'/videos/record'
        f_mono1=name+'_mono1.h264'
        f_mono2=name+'_mono2.h264'
        f_color=name+'_color.h264'
        start=time.time()
        print("RECORDING for"+ camName + " started at "+str(int(time.time())) + " seconds.")
        with open(f_mono1, 'wb') as fileMono1H264, open(f_color, 'wb') as fileColorH265, open(f_mono2, 'wb') as fileMono2H264:
#             print("Press Ctrl+C or interrupt kernel to stop encoding...")
            
            while (time.time()-start<time_limit+2):
#                 print(time.time()-start)
                try:
                    # Empty each queue
                    while outQ1.has():
#                         print("11"+str(outQ1.has()))
                        outQ1.get().getData().tofile(fileMono1H264)

#                     while outQ2.has():
# #                         print("21"+str(outQ2.has()))
#                         outQ2.get().getData().tofile(fileColorH265)

                    while outQ3.has():
#                         print("31"+str(outQ3.has()))
                        outQ3.get().getData().tofile(fileMono2H264)
    
                except KeyboardInterrupt:
                    # Keyboard interrupt (Ctrl + C) detected
                    break
        print("Converting to mp4...")
        cmd = "ffmpeg -framerate 30 -i {} -c copy {}"

        os.system(cmd.format(f_mono1,name+'_mono1.mp4'))
        os.system(cmd.format(f_mono2, name+'_mono2.mp4'))
        os.system(cmd.format(f_color, name+"_color.mp4"))
        time.sleep(5)
        print("Conversion complete. Removing temporary files")

        os.remove(f_mono1)
        os.remove(f_mono2)
        os.remove(f_color)
        
        print("RECORDING for "+ camName + " ended at "+str(int(time.time())) + " seconds.")
if __name__=="__main__":
    streamName1=['ve1Out','ve2Out','ve3Out']
    streamName2=['ve1Out1','ve2Out1','ve3Out1']
    config=getConfigData("config.json").get_record_config()
    ray.init()
    month,day,year=time.localtime().tm_mon,time.localtime().tm_mday,time.localtime().tm_year
    hour,minutes,seconds=time.localtime().tm_hour,time.localtime().tm_min,time.localtime().tm_sec
    dir_name=str(month)+'_'+str(day)+'_'+str(year)+'_'+str(hour)+str(minutes)
    path=config['data_path']+'/'+dir_name
    os.mkdir(path)
    ray.get([recordCam.remote(mxID = '14442C10913365D300',path = path,streamName = streamName1,camName = 'cam1',time_limit = int(config['time_limit'])),
             recordCam.remote(mxID = '14442C10810665D300',path = path,streamName = streamName2,camName = 'cam2',time_limit = int(config['time_limit']))])
    ray.shutdown()  