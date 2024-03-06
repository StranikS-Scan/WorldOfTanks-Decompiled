# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/hints/battle/schemas/base.py
import typing
import logging
from dict2model import models
from dict2model import schemas
from dict2model import fields
from dict2model import validate
from dict2model import exceptions
from constants import IS_DEVELOPMENT, IS_VS_EDITOR
from hints_common.battle.schemas.base import CommonHintSchema, CommonHintModel, HMCPropsType, HMCContextType
from hints.battle.schemas.const import HTML_TEMPLATE_PATH, MIN_SHOW_TIME_LOWER_LIMIT, MIN_SHOW_TIME_UPPER_LIMIT, DEFAULT_MIN_SHOW_TIME, DEFAULT_WAIT_TIME, DEFAULT_SHOW_TIME, DEFAULT_COOLDOWN_TIME
from helpers import i18n, dependency
from gui import makeHtmlString, g_htmlTemplates
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType
    from hints_common.battle.schemas.base import CommonHintPropsSchema
_logger = logging.getLogger(__name__)

class ClientHintTextModel(models.Model):
    __slots__ = ('raw', 'key', 'template', 'highlight', '_message')

    def __init__(self, raw, key, template, highlight):
        super(ClientHintTextModel, self).__init__()
        self.raw = raw
        self.key = key
        self.template = template
        self.highlight = highlight
        self._message = self._createMessage(self.raw, self.key, self.template)

    @property
    def message(self):
        return self._message

    @staticmethod
    def _createMessage(raw='', key='', template=''):
        return raw or (i18n.makeString(key) if key else '') or (makeHtmlString(HTML_TEMPLATE_PATH, template) if template else '')

    def _reprArgs(self):
        return 'raw={}, key={}, template={}, highlight={}, msg={}'.format(self.raw, self.key, self.template, self.highlight, self._message)


class ClientHintVisualModel(models.Model):
    __slots__ = ('image',)

    def __init__(self, image):
        super(ClientHintVisualModel, self).__init__()
        self.image = image

    def _reprArgs(self):
        return 'image={}'.format(self.image)


class ClientHintSoundModel(models.Model):
    __slots__ = ('fx', 'notify')

    def __init__(self, fx, notify):
        super(ClientHintSoundModel, self).__init__()
        self.fx = fx
        self.notify = notify

    def createFx(self):
        try:
            return self._createFx()
        except Exception as error:
            _logger.error('Sound fx creation error: %s.', error)
            return ''

    def createNotify(self):
        try:
            return self._createNotify()
        except Exception as error:
            _logger.error('Sound notify creation error: %s.', error)
            return ''

    def _createFx(self):
        return self.fx

    def _createNotify(self):
        return self.notify

    def _reprArgs(self):
        return 'fx={}, notify={}'.format(self.fx, self.notify)


class ClientHintLifecycleModel(models.Model):
    __slots__ = ('showTime', 'minShowTime', 'waitTime')

    def __init__(self, showTime, minShowTime, waitTime):
        super(ClientHintLifecycleModel, self).__init__()
        self.showTime = showTime
        self.minShowTime = minShowTime
        self.waitTime = waitTime

    def _reprArgs(self):
        return 'showTime={}, minShowTime={}, waitTime={}'.format(self.showTime, self.minShowTime, self.waitTime)


class ClientHintHistoryModel(models.Model):
    __slots__ = ('modifyPriority', 'cooldown')

    def __init__(self, modifyPriority, cooldown):
        super(ClientHintHistoryModel, self).__init__()
        self.modifyPriority = modifyPriority
        self.cooldown = cooldown

    def _reprArgs(self):
        return 'modifyPriority={}, cooldown={}'.format(self.modifyPriority, self.cooldown)


CHMTextType = typing.TypeVar('CHMTextType', bound=ClientHintTextModel)
CHMVisualType = typing.TypeVar('CHMVisualType', bound=ClientHintVisualModel)
CHMSoundType = typing.TypeVar('CHMSoundType', bound=ClientHintSoundModel)
CHMLifecycleType = typing.TypeVar('CHMLifecycleType', bound=ClientHintLifecycleModel)
CHMHistoryType = typing.TypeVar('CHMHistoryType', bound=ClientHintHistoryModel)

class ClientHintModel(CommonHintModel[HMCPropsType, HMCContextType], typing.Generic[HMCPropsType, HMCContextType, CHMTextType, CHMVisualType, CHMSoundType, CHMLifecycleType, CHMHistoryType]):
    __slots__ = ('text', 'visual', 'sound', 'lifecycle', 'history')
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, props, context, text, visual, sound, lifecycle, history):
        super(ClientHintModel, self).__init__(props=props, context=context)
        self.text = text
        self.visual = visual
        self.sound = sound
        self.lifecycle = lifecycle
        self.history = history

    def validate(self, *args, **kwargs):
        visitor = self._sessionProvider.arenaVisitor
        return super(ClientHintModel, self).validate(visitor.getArenaBonusType(), visitor.type.getGamePlayName(), *args, **kwargs)

    def canBeShown(self):
        return True

    def createVO(self, data=None):
        data = data or {}
        try:
            return self._createVO(data)
        except Exception as error:
            _logger.error('[%s] value object creation error: %s.', self.uniqueName, error)
            return {}

    def _createVO(self, data):
        message = self._formatMessage(self.text.message, data) if self.text and self.text.message else ''
        messageHighlight = self.text.highlight if self.text else ''
        iconSource = self.visual.image if self.visual and self.visual.image else ''
        if not message and not iconSource:
            _logger.debug('[%s] missing visual.', self.uniqueName)
            return {}
        context = self.context.create(data) if self.context else {}
        return {'message': message,
         'messageHighlight': messageHighlight,
         'iconSource': iconSource,
         'context': context}

    def _formatMessage(self, message, data):
        try:
            return message.format(**data)
        except KeyError:
            _logger.error('[%s]. Incorrect message format for: %s', self.uniqueName, str(data))

    def _reprArgs(self):
        return '{}, {}'.format(super(ClientHintModel, self)._reprArgs(), 'text={}, visual={}, sound={}, lifecycle={}, history={}'.format(self.text, self.visual, self.sound, self.lifecycle, self.history))


CHMType = typing.TypeVar('CHMType', bound=ClientHintModel)

def validateHintTextKey(key):
    if not i18n.isValidKey(key):
        raise exceptions.ValidationError('Wrong localization key format. Example: #feature:hints/fire.')


def validateHintTextTemplate(key):
    templates = g_htmlTemplates[HTML_TEMPLATE_PATH]
    if not templates:
        raise exceptions.ValidationError('No templates by path: {}.'.format(HTML_TEMPLATE_PATH))


def validateHintTextModel(model):
    if not (IS_DEVELOPMENT or IS_VS_EDITOR) and model.raw:
        raise exceptions.ValidationError('Raw text disabled for production mode.')
    count = sum([ 1 for text in (model.raw, model.key, model.template) if text ])
    if count <= 0:
        raise exceptions.ValidationError('Text not provided.')
    elif count != 1:
        raise exceptions.ValidationError('More than one text source provided.')


def validateLifecycleModel(model):
    if model.showTime and model.showTime < model.minShowTime:
        raise exceptions.ValidationError('ShowTime less than minShowTime.')


def validateHintModel(model):
    if not model.text and not model.visual and not model.sound:
        raise exceptions.ValidationError('Provide text or visual or sound filed.')


class ClientHintTextSchema(schemas.Schema[CHMTextType]):
    __slots__ = ()

    def __init__(self, modelClass=ClientHintTextModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        super(ClientHintTextSchema, self).__init__(fields={'raw': fields.String(required=False, default='', deserializedValidators=validate.Length(minValue=1, maxValue=500)),
         'key': fields.String(required=False, default='', deserializedValidators=[validate.Length(minValue=1, maxValue=100), validateHintTextKey]),
         'template': fields.String(required=False, default='', deserializedValidators=[validate.Length(minValue=1, maxValue=100), validateHintTextTemplate]),
         'highlight': fields.String(required=False, default='', deserializedValidators=validate.Length(minValue=1, maxValue=100))}, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=[validateHintTextModel] + validate.prepareValidators(deserializedValidators), modelClass=modelClass)


class ClientHintVisualSchema(schemas.Schema[CHMVisualType]):
    __slots__ = ()

    def __init__(self, modelClass=ClientHintVisualModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        super(ClientHintVisualSchema, self).__init__(fields={'image': fields.String(required=False, default='', deserializedValidators=validate.Length(minValue=1, maxValue=100))}, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators, modelClass=modelClass)


class ClientHintSoundSchema(schemas.Schema[CHMSoundType]):
    __slots__ = ()

    def __init__(self, modelClass=ClientHintSoundModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        super(ClientHintSoundSchema, self).__init__(fields={'fx': fields.String(required=False, default='', deserializedValidators=validate.Length(minValue=1, maxValue=100)),
         'notify': fields.String(required=False, default='', deserializedValidators=validate.Length(minValue=1, maxValue=100))}, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators, modelClass=modelClass)


class ClientHintHistorySchema(schemas.Schema[CHMHistoryType]):
    __slots__ = ()

    def __init__(self, modelClass=ClientHintHistoryModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        super(ClientHintHistorySchema, self).__init__(fields={'modifyPriority': fields.Boolean(required=False, default=False),
         'cooldown': fields.Float(required=False, default=DEFAULT_COOLDOWN_TIME, deserializedValidators=validate.Range(minValue=0))}, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators, modelClass=modelClass)


clientHintTextSchema = ClientHintTextSchema()
clientHintVisualSchema = ClientHintVisualSchema()
clientHintSoundSchema = ClientHintSoundSchema()
clientHintHistorySchema = ClientHintHistorySchema()
clientHintLifecycleSchema = schemas.Schema[ClientHintLifecycleModel](fields={'showTime': fields.Float(required=False, default=DEFAULT_SHOW_TIME, deserializedValidators=validate.Range(minValue=0)),
 'minShowTime': fields.Float(required=False, default=DEFAULT_MIN_SHOW_TIME, deserializedValidators=validate.Range(minValue=MIN_SHOW_TIME_LOWER_LIMIT, maxValue=MIN_SHOW_TIME_UPPER_LIMIT)),
 'waitTime': fields.Float(required=False, default=DEFAULT_WAIT_TIME, deserializedValidators=validate.Range(minValue=0))}, checkUnknown=True, deserializedValidators=validateLifecycleModel, modelClass=ClientHintLifecycleModel)

class ClientHintSchema(CommonHintSchema[CHMType]):
    __slots__ = ('textSchema', 'visualSchema', 'soundSchema', 'historySchema')

    def __init__(self, modelClass=ClientHintModel, propsSchema=None, contextSchema=None, textSchema=None, visualSchema=None, soundSchema=None, historySchema=None, serializedValidators=None, deserializedValidators=None):
        super(ClientHintSchema, self).__init__(propsSchema=propsSchema, contextSchema=contextSchema, serializedValidators=serializedValidators, deserializedValidators=[validateHintModel] + validate.prepareValidators(deserializedValidators), modelClass=modelClass)
        self.textSchema = textSchema or clientHintTextSchema
        self.visualSchema = visualSchema or clientHintVisualSchema
        self.soundSchema = soundSchema or clientHintSoundSchema
        self.historySchema = historySchema or clientHintHistorySchema
        self._fields['text'] = fields.Nested(required=False, schema=self.textSchema, default=None)
        self._fields['visual'] = fields.Nested(required=False, schema=self.visualSchema, default=None)
        self._fields['sound'] = fields.Nested(required=False, schema=self.soundSchema, default=None)
        self._fields['lifecycle'] = fields.Nested(required=False, schema=clientHintLifecycleSchema, default=ClientHintLifecycleModel(showTime=DEFAULT_SHOW_TIME, minShowTime=DEFAULT_MIN_SHOW_TIME, waitTime=DEFAULT_WAIT_TIME))
        self._fields['history'] = fields.Nested(required=False, schema=self.historySchema, default=None)
        return


clientHintSchema = ClientHintSchema()
