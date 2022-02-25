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
        self.config_record=getConfigData().get_record_config()
        print(self.config_record)
    def setup_pipeline(self):
        pipeline = dai.Pipeline()
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

        ve1Out.setStreamName('ve1Out')
        ve2Out.setStreamName('ve2Out')
        ve3Out.setStreamName('ve3Out')

        # Properties
        camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
        monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        video_enc_props={'H264_HIGH':dai.VideoEncoderProperties.Profile.H264_HIGH,
                         'H264_BASELINE':dai.VideoEncoderProperties.Profile.H264_BASELINE,
                         'H264_MAIN':dai.VideoEncoderProperties.Profile.H264_MAIN,
                         'MJPEG':dai.VideoEncoderProperties.Profile.MJPEG}
        # Create encoders, one for each camera, consuming the frames and encoding them using H.264 / H.265 encoding
        ve1.setDefaultProfilePreset(self.config_record['frame_rate'], video_enc_props[self.config_record['video_encoder_prop']])
        ve2.setDefaultProfilePreset(self.config_record['frame_rate'], video_enc_props[self.config_record['video_encoder_prop']])
        ve3.setDefaultProfilePreset(self.config_record['frame_rate'], video_enc_props[self.config_record['video_encoder_prop']])

        # Linking
        monoLeft.out.link(ve1.input)
        camRgb.video.link(ve2.input)
        monoRight.out.link(ve3.input)
        ve1.bitstream.link(ve1Out.input)
        ve2.bitstream.link(ve2Out.input)
        ve3.bitstream.link(ve3Out.input)

        return pipeline

# if __name__=="__main__":
#     pipeline=Pipeline()