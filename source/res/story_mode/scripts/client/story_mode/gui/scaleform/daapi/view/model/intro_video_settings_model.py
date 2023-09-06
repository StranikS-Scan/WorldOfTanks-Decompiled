# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/model/intro_video_settings_model.py
import ResMgr
import section2dict
from dict2model import models, schemas, fields
INTRO_VIDEO_SETTINGS_PATH = 'story_mode/gui/intro_video.xml'

class SoundEventsModel(models.Model):
    __slots__ = ('start', 'pause', 'resume', 'stop')

    def __init__(self, start, pause, resume, stop):
        super(SoundEventsModel, self).__init__()
        self.start = start
        self.pause = pause
        self.resume = resume
        self.stop = stop


class IntroVideoSettingsModel(models.Model):
    __slots__ = ('videoPath', 'music', 'vo')

    def __init__(self, videoPath, music, vo):
        super(IntroVideoSettingsModel, self).__init__()
        self.videoPath = videoPath
        self.music = music
        self.vo = vo


soundEventSchema = schemas.Schema(fields={'start': fields.String(required=True),
 'pause': fields.String(required=False, default=''),
 'resume': fields.String(required=False, default=''),
 'stop': fields.String(required=False, default='')}, modelClass=SoundEventsModel, checkUnknown=True)
introVideoSchema = schemas.Schema(fields={'videoPath': fields.String(required=True),
 'music': fields.Nested(soundEventSchema, required=True),
 'vo': fields.String(required=True)}, modelClass=IntroVideoSettingsModel, checkUnknown=True)
__introVideoSchema = None

def getSettings():
    global __introVideoSchema
    if __introVideoSchema:
        return __introVideoSchema
    root = ResMgr.openSection(INTRO_VIDEO_SETTINGS_PATH)
    rawData = section2dict.parse(root)
    __introVideoSchema = introVideoSchema.deserialize(rawData)
    return __introVideoSchema
