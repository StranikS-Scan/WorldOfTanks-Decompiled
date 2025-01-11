# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/universal_flag_entry_point_controller/config.py
import logging
import typing
from skeletons.gui.game_control import IUniversalFlagEntryPointController
from dict2model import fields, schemas
from dict2model.models import Model
from dict2model.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class MissionsMarathonTarget(object):
    __slots__ = ('marathonPrefix',)

    def __init__(self, marathonPrefix):
        self.marathonPrefix = marathonPrefix


class FullScreenBrowserTarget(object):
    __slots__ = ('url',)

    def __init__(self, url):
        self.url = url


class ShopPageTarget(object):
    __slots__ = ('relativeUrl',)

    def __init__(self, relativeUrl):
        self.relativeUrl = relativeUrl


class NopeTarget(object):
    __slots__ = tuple()


class UniversalFlagTimer(Model):
    __slots__ = ('time', 'iconType', 'text')

    def __init__(self, time=0, iconType=IUniversalFlagEntryPointController.TimerIconType.NONE, text=''):
        super(UniversalFlagTimer, self).__init__()
        self.time = time
        self.iconType = iconType
        self.text = text


class UniversalFlagState(Model):
    __slots__ = ('startTime', 'finishTime', 'caption', 'description', 'background', 'timer', 'tooltipBackground')

    def __init__(self, startTime=0, finishTime=0, caption='', description='', background=None, tooltipBackground='', timer=None):
        super(UniversalFlagState, self).__init__()
        self.startTime = startTime
        self.finishTime = finishTime
        self.caption = caption
        self.description = description
        self.background = background if background else IUniversalFlagEntryPointController.FlagBackground()
        self.timer = timer if timer else UniversalFlagTimer()
        self.tooltipBackground = tooltipBackground


class UniversalFlagConfig(Model):

    def __init__(self, isEnabled=False, isPaused=False, target=None, states=None, showTime=0, hideTime=0):
        super(UniversalFlagConfig, self).__init__()
        self.isEnabled = isEnabled
        self.isPaused = isPaused
        self.target = target
        self.states = states if states else []
        self.showTime = showTime
        self.hideTime = hideTime


class _BackgroundField(fields.Field):

    def _deserialize(self, incoming, **kwargs):
        result = IUniversalFlagEntryPointController.FlagBackground()
        result.active = incoming['active']
        result.activeHover = incoming['activeHover']
        result.disabled = incoming['disabled']
        result.disabledHover = incoming['disabledHover']
        return result

    def _serialize(self, incoming, **kwargs):
        return {'active': incoming.active,
         'activeHover': incoming.activeHover,
         'disabled': incoming.disabled,
         'disabledHover': incoming.disabledHover}


class _TargetField(fields.Field):

    def _deserialize(self, incoming, **kwargs):
        if 'missionsMarathon' in incoming:
            return MissionsMarathonTarget(incoming['missionsMarathon'])
        if 'fullScreenBrowser' in incoming:
            return FullScreenBrowserTarget(incoming['fullScreenBrowser'])
        if 'shopPage' in incoming:
            return ShopPageTarget(incoming['shopPage'])
        if 'nope' in incoming:
            return NopeTarget()
        raise fields.ValidationError('Invalid flag entry point target config')

    def _serialize(self, incoming, **kwargs):
        if isinstance(incoming, MissionsMarathonTarget):
            return {'missionsMarathon': incoming.marathonPrefix}
        elif isinstance(incoming, FullScreenBrowserTarget):
            return {'fullScreenBrowser': incoming.url}
        elif isinstance(incoming, ShopPageTarget):
            return {'shopPage': incoming.relativeUrl}
        elif isinstance(incoming, NopeTarget):
            return {'nope': None}
        else:
            raise ValidationError('Wrong target type.')
            return None


universalFlagTimerSchema = schemas.Schema(fields={'time': fields.Integer(required=True),
 'iconType': fields.Enum(IUniversalFlagEntryPointController.TimerIconType, required=True),
 'text': fields.String(required=True)}, modelClass=UniversalFlagTimer, checkUnknown=True)
universalFlagStateSchema = schemas.Schema(fields={'startTime': fields.Integer(required=True),
 'finishTime': fields.Integer(required=True),
 'background': _BackgroundField(required=True),
 'caption': fields.String(required=True),
 'description': fields.String(required=True),
 'tooltipBackground': fields.String(required=True),
 'timer': fields.Nested(schema=universalFlagTimerSchema, required=True)}, modelClass=UniversalFlagState, checkUnknown=True)
universalFlagConfigSchema = schemas.Schema(fields={'isEnabled': fields.Boolean(required=True),
 'isPaused': fields.Boolean(required=True),
 'target': _TargetField(required=True),
 'states': fields.List(universalFlagStateSchema, required=True)}, modelClass=UniversalFlagConfig, checkUnknown=True)
