from utils.getConfig import getConfigData
import ray
from pipeline.pipeline import Pipeline
import os
import time
import sys
from playsound import playsound
import json
import random
from os import listdir
import pygame

try:
    import depthai as dai
except:
    print("Run \"python3 install_requirements.py\" to install dependencies or follow README for setup instructions")
    sys.exit(42)


def getPipeLine(streamName):
    pipeline = dai.Pipeline()
    config=getConfigData("config.json").get_record_config()
    # Define sources and outputs
    camRgb = pipeline.create(dai.node.ColorCamera)
    monoLeft = pipeline.create(dai.node.MonoCamera)
    monoRight = pipeline.create(dai.node.MonoCamera)
    ve1 = pipeline.create(dai.node.VideoEncoder)
    ve2 = pipeline.create(dai.node.VideoEncoder)
    ve3 = pipeline.create(dai.node.VideoEncoder)

    ve1Out = pipeline.create(dai.node.XLinkOut)
    ve2Out = pipeline.create(dai.node.XLinkOut)
    ve3Out = pipeline.create(dai.node.XLinkOut)

    ve1Out.setStreamName(streamName[0])
    ve2Out.setStreamName(streamName[1])
    ve3Out.setStreamName(streamName[2])

    # Properties
    camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
    monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    # Create encoders, one for each camera, consuming the frames and encoding them using H.264 / H.265 encoding
    color_fps=60
    if(config['fps']<60):
        color_fps=config['fps']
    ve1.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H264_HIGH)
    ve2.setDefaultProfilePreset(config['fps'], dai.VideoEncoderProperties.Profile.H264_HIGH)
    ve3.setDefaultProfilePreset(config['fps'], dai.VideoEncoderProperties.Profile.H264_HIGH)

    # Linking
    monoLeft.out.link(ve2.input)
    camRgb.video.link(ve1.input)
    monoRight.out.link(ve3.input)
    ve1.bitstream.link(ve1Out.input)
    ve2.bitstream.link(ve2Out.input)
    ve3.bitstream.link(ve3Out.input)
    return pipeline

@ray.remote
def recordCam(mxID,path,streamName,camName,time_limit):
    pipeline=getPipeLine(streamName)
    isDev1,deviceInfo=dai.Device.getDeviceByMxId(mxID)
    with dai.Device(pipeline,deviceInfo) as dev:

        # Output queues will be used to get the encoded data from the outputs defined above
        outQ_mono_1 = dev.getOutputQueue(name=streamName[1], maxSize=30, blocking=False)
        outQ_color = dev.getOutputQueue(name=streamName[0], maxSize=30, blocking=False)
        outQ_mono_2 = dev.getOutputQueue(name=streamName[2], maxSize=30, blocking=False)
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
                    while outQ_mono_1.has():
#                         print("11"+str(outQ1.has()))
                        outQ_mono_1.get().getData().tofile(fileMono1H264)

                    while outQ_color.has():
#                         print("21"+str(outQ2.has()))
                        outQ_color.get().getData().tofile(fileColorH265)

                    while outQ_mono_2.has():
#                         print("31"+str(outQ3.has()))
                        outQ_mono_2.get().getData().tofile(fileMono2H264)
    
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

def recordVideo(path,streamName1,streamName2,config,currentRun,audio_path):
    ray.init()
    os.mkdir(path)
    # ray.get([recordCam.remote(mxID = '14442C10913365D300',path = path,streamName = streamName1,camName = 'cam1',time_limit = int(config['time_limit'])),
    #          recordCam.remote(mxID = '14442C10810665D300',path = path,streamName = streamName2,camName = 'cam2',time_limit = int(config['time_limit'])),
    #          playAudio.remote(audio_path)])
    ray.shutdown()
    currentRun['timeEnd']=time.time()
    saveJson(currentRun,path+'/metadata.json')
    saveJson(currentRun,'./lastRunMeta.json')

def saveJson(currentRun,path):
    jsonObj=json.dumps(currentRun)
    with open(path,"w") as file:
        file.write(jsonObj)

def getLastRunTime(lastRun):
    return lastRun['timeStart']
@ray.remote
def playAudio(audio_path):
    time.sleep(10)
    print(f'Playing Audio: {audio_path}')
    playAudio(audio_path)
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
if __name__=="__main__":
    
    config=getConfigData("config.json").get_record_config()
    audio_files_list=listdir(config['audio_path'])
    session_id=input("Enter Session ID: ")
    try:
        while len(audio_files_list)>0:
            lastRunMetaPath='./lastRunMeta.json'
            with open(lastRunMetaPath,'rb') as file:
                lastRun=json.load(file)
            streamName1=['ve1Out','ve2Out','ve3Out']
            streamName2=['ve1Out1','ve2Out1','ve3Out1']
            month,day,year=time.localtime().tm_mon,time.localtime().tm_mday,time.localtime().tm_year
            hour,minutes,seconds=time.localtime().tm_hour,time.localtime().tm_min,time.localtime().tm_sec
            dir_name=str(month)+'_'+str(day)+'_'+str(year)+'_'+str(hour)+str(minutes)+'_'+session_id
            path=config['data_path']+'/'+dir_name
            lastRunTime=getLastRunTime(lastRun)
            randomFlag=random.randint(0,100)%7==0
            audio_file=random.choice(audio_files_list)
            audio_files_list.remove(audio_file)
            audio_path=config['audio_path']+audio_file
            currentRun={
                "timeStart":time.time(),
                "audio_path":audio_path,
                "path":path,
                "year":year,
                "month":month,
                "day":day,
                "timeEnd":time.time()
            }
            if(time.time()-lastRunTime>config['trial_interval'] and randomFlag):
                currentRun['timeStart']=time.time()
                recordVideo(path=path,streamName1=streamName1,streamName2=streamName2,config=config,currentRun=currentRun,audio_path=audio_path)
                
    except KeyboardInterrupt:
        print("Recording Stopped")

