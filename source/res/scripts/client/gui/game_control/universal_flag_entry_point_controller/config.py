# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/universal_flag_entry_point_controller/config.py
import logging
import operator
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


class TopSubBrowserTarget(object):
    __slots__ = ('url',)

    def __init__(self, url):
        self.url = url


class NopeTarget(object):
    __slots__ = tuple()


class ShowGoldWagonTarget(object):
    __slots__ = tuple()


class TokenOperation(object):
    __slots__ = ('_operationType', '_expectedAmount')
    TOKEN_OPERATION_MAPPING = {'less': operator.lt,
     'greater': operator.gt,
     'equal': operator.eq,
     'lessOrEqual': operator.le,
     'greaterOrEqual': operator.ge}

    def __init__(self, operationType, expectedAmount):
        self._operationType = operationType
        self._expectedAmount = expectedAmount


class BaseProgressStateToken(TokenOperation):
    __slots__ = ('_tokenName', '_amount')

    def __init__(self, tokenName, operationType, expectedAmount):
        self._tokenName = tokenName
        self._amount = None
        super(BaseProgressStateToken, self).__init__(operationType=operationType, expectedAmount=expectedAmount)
        return

    def getAmount(self):
        return self._amount

    def update(self, tokens):
        raise NotImplementedError('BaseProgressStateToken.update() not implemented')

    def checkCompareAmountWithExpected(self):
        return self.TOKEN_OPERATION_MAPPING[self._operationType](self._amount, self._expectedAmount)


class ProgressStateToken(BaseProgressStateToken):

    def __init__(self, tokenName, operationType, expectedAmount):
        super(ProgressStateToken, self).__init__(tokenName=tokenName, operationType=operationType, expectedAmount=expectedAmount)

    def update(self, tokens):
        newAmount = 0
        token = tokens.getToken(self._tokenName)
        if token:
            newAmount = token[1]
        if self._amount == newAmount:
            return False
        self._amount = newAmount
        return True


class ProgressStateExpirationToken(BaseProgressStateToken):
    _slots__ = ('__expiration',)

    def __init__(self, tokenName, operationType, expectedAmount):
        self.__expiration = None
        super(ProgressStateExpirationToken, self).__init__(tokenName=tokenName, operationType=operationType, expected_amount=expectedAmount)
        return

    def getExpiration(self):
        return self.__expiration

    def update(self, tokens):
        newAmount = 0
        newExpiration = None
        token = tokens.getToken(self._tokenName)
        if token:
            newExpiration = token[0]
            newAmount = token[1]
        if self._amount == newAmount and self.__expiration == newExpiration:
            return False
        else:
            self._amount = newAmount
            self.__expiration = newExpiration
            return True


class UniversalFlagTimer(Model):
    __slots__ = ('time', 'iconType', 'text')

    def __init__(self, time=0, iconType=IUniversalFlagEntryPointController.TimerIconType.NONE, text=''):
        super(UniversalFlagTimer, self).__init__()
        self.time = time
        self.iconType = iconType
        self.text = text


class UniversalFlagState(Model):
    __slots__ = ('startTime', 'finishTime', 'caption', 'description', 'background', 'timer', 'tooltipBackground', 'target', 'token')

    def __init__(self, startTime=0, finishTime=0, caption='', description='', background=None, tooltipBackground='', timer=None, target=None, token=None):
        super(UniversalFlagState, self).__init__()
        self.startTime = startTime
        self.finishTime = finishTime
        self.caption = caption
        self.description = description
        self.background = background if background else IUniversalFlagEntryPointController.FlagBackground()
        self.timer = timer if timer else UniversalFlagTimer()
        self.tooltipBackground = tooltipBackground
        self.target = target
        self.token = token


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
        if 'topSubBrowser' in incoming:
            return TopSubBrowserTarget(incoming['topSubBrowser'])
        if 'nope' in incoming:
            return NopeTarget()
        if 'showGoldWagon' in incoming:
            return ShowGoldWagonTarget()
        raise fields.ValidationError('Invalid flag entry point target config')

    def _serialize(self, incoming, **kwargs):
        if isinstance(incoming, MissionsMarathonTarget):
            return {'missionsMarathon': incoming.marathonPrefix}
        elif isinstance(incoming, FullScreenBrowserTarget):
            return {'fullScreenBrowser': incoming.url}
        elif isinstance(incoming, ShopPageTarget):
            return {'shopPage': incoming.relativeUrl}
        elif isinstance(incoming, TopSubBrowserTarget):
            return {'topSubBrowser': incoming.url}
        elif isinstance(incoming, NopeTarget):
            return {'nope': None}
        elif isinstance(incoming, ShowGoldWagonTarget):
            return {'showGoldWagon': None}
        else:
            raise ValidationError('Wrong target type.')
            return None


class _TokenField(fields.Field):

    def _deserialize(self, incoming, **kwargs):
        if 'progressStateToken' in incoming and 'operationType' in incoming:
            return ProgressStateToken(tokenName=incoming['progressStateToken'], operationType=incoming['operationType'], expectedAmount=incoming['expectedAmount'])
        if 'progressStateExpirationToken' in incoming and 'operationType' in incoming:
            return ProgressStateExpirationToken(tokenName=incoming['progressStateExpirationToken'], operationType=incoming['operationType'], expectedAmount=incoming['expectedAmount'])
        raise fields.ValidationError('Invalid flag entry point token config')

    def _serialize(self, incoming, **kwargs):
        if isinstance(incoming, ProgressStateToken):
            return {'progressStateTokenAmount': incoming.getAmount()}
        if isinstance(incoming, ProgressStateExpirationToken):
            return {'progressStateExpirationTokenAmount': incoming.getAmount(),
             'progressStateExpirationTokenExpiration': incoming.getExpiration()}
        raise ValidationError('Wrong token type.')


universalFlagTimerSchema = schemas.Schema(fields={'time': fields.Integer(required=True),
 'iconType': fields.Enum(IUniversalFlagEntryPointController.TimerIconType, required=True),
 'text': fields.String(required=True)}, modelClass=UniversalFlagTimer, checkUnknown=True)
universalFlagStateSchema = schemas.Schema(fields={'startTime': fields.Integer(required=True),
 'finishTime': fields.Integer(required=True),
 'background': _BackgroundField(required=True),
 'caption': fields.String(required=True),
 'description': fields.String(required=True),
 'tooltipBackground': fields.String(required=True),
 'timer': fields.Nested(schema=universalFlagTimerSchema, required=True),
 'target': _TargetField(required=False),
 'token': _TokenField(required=False)}, modelClass=UniversalFlagState, checkUnknown=True)
universalFlagConfigSchema = schemas.Schema(fields={'isEnabled': fields.Boolean(required=True),
 'isPaused': fields.Boolean(required=True),
 'target': _TargetField(required=True),
 'states': fields.List(universalFlagStateSchema, required=True)}, modelClass=UniversalFlagConfig, checkUnknown=True)
