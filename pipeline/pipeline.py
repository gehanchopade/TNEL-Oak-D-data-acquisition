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
        self.config=getConfigData("./config.json").get_record_config()
    def getPipeLine(self,streamName):
        pipeline = dai.Pipeline()

        # Define sources and outputs
        if(self.config['color_cam']):
            camRgb = pipeline.create(dai.node.ColorCamera)
            ve_color = pipeline.create(dai.node.VideoEncoder)
            ve_color_Out = pipeline.create(dai.node.XLinkOut)
            ve_color_Out.setStreamName(streamName[0])
            camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
            if(self.config['fps']>60):
                color_fps=60
            else:
                color_fps=self.config['fps']
            ve_color.setDefaultProfilePreset(color_fps, dai.VideoEncoderProperties.Profile.H264_HIGH)
            camRgb.video.link(ve_color.input)
            ve_color.bitstream.link(ve_color_Out.input)

        if(self.config['mono1']):
            monoLeft = pipeline.create(dai.node.MonoCamera)
            ve_mono_left = pipeline.create(dai.node.VideoEncoder)
            ve_mono_left_Out = pipeline.create(dai.node.XLinkOut)
            ve_mono_left_Out.setStreamName(streamName[1])
            monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
            ve_mono_left.setDefaultProfilePreset(self.config['fps'], dai.VideoEncoderProperties.Profile.H264_HIGH)
            monoLeft.out.link(ve_mono_left.input)
            ve_mono_left.bitstream.link(ve_mono_left_Out.input)

        if(self.config['mono2']):
            monoRight = pipeline.create(dai.node.MonoCamera)    
            ve_mono_right = pipeline.create(dai.node.VideoEncoder)
            ve_mono_right_Out = pipeline.create(dai.node.XLinkOut)
            ve_mono_right_Out.setStreamName(streamName[2])
            monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)
            ve_mono_right.setDefaultProfilePreset(self.config['fps'], dai.VideoEncoderProperties.Profile.H264_HIGH)
            monoRight.out.link(ve_mono_right.input)
            ve_mono_right.bitstream.link(ve_mono_right_Out.input)

        return pipeline


# if __name__=="__main__":
#     pipeline=Pipeline()
