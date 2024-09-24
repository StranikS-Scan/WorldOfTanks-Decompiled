# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/model/intro_video_settings_model.py
import ResMgr
import section2dict
import typing
from dict2model import models, schemas, fields, validate
from story_mode_common.configs.sounds_schema import SoundModel, SoundSchema
INTRO_VIDEO_SETTINGS_PATH = 'story_mode/gui/intro_video.xml'

class SoundEventsModel(SoundModel):
    __slots__ = ('pause', 'resume')

    def __init__(self, start, pause, resume, stop, group, state):
        super(SoundEventsModel, self).__init__(start, stop, group, state)
        self.pause = pause
        self.resume = resume


class SoundEventsSchema(SoundSchema[SoundEventsModel]):

    def __init__(self):
        super(SoundEventsSchema, self).__init__(fields={'pause': fields.String(required=True, default=''),
         'resume': fields.String(required=True, default='')}, checkUnknown=True, modelClass=SoundEventsModel)


soundEventsSchema = SoundEventsSchema()

class VideoModel(models.Model):
    __slots__ = ('id', 'videoPath', 'music', 'playSoundOnClose', 'vo')

    def __init__(self, id, videoPath, music, playSoundOnClose, vo):
        super(VideoModel, self).__init__()
        self.id = id
        self.videoPath = videoPath
        self.music = music
        self.playSoundOnClose = playSoundOnClose
        self.vo = vo


class IntroVideoSettingsModel(models.Model):
    __slots__ = ('missions',)

    def __init__(self, missions):
        super(IntroVideoSettingsModel, self).__init__()
        self.missions = missions


videoSchema = schemas.Schema(fields={'id': fields.Integer(required=True, deserializedValidators=validate.Range(minValue=1)),
 'videoPath': fields.String(required=True),
 'music': fields.Nested(soundEventsSchema, required=True),
 'playSoundOnClose': fields.String(required=False),
 'vo': fields.String(required=True)}, modelClass=VideoModel, checkUnknown=True)
introVideoSchema = schemas.Schema(fields={'missions': fields.UniCapList(fieldOrSchema=videoSchema, required=True, deserializedValidators=validate.Length(minValue=1))}, modelClass=IntroVideoSettingsModel, checkUnknown=True)
__introVideoSchema = None

def getSettings():
    global __introVideoSchema
    if __introVideoSchema:
        return __introVideoSchema
    root = ResMgr.openSection(INTRO_VIDEO_SETTINGS_PATH)
    rawData = section2dict.parse(root)
    __introVideoSchema = introVideoSchema.deserialize(rawData)
    return __introVideoSchema
