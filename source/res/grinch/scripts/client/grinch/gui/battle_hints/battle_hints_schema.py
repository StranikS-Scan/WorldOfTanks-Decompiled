# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_hints/battle_hints_schema.py
import typing
from dict2model import fields
from hints.battle.schemas.base import ClientHintTextModel, ClientHintModel, CHMLifecycleType, CHMVisualType, CHMSoundType, ClientHintSchema, ClientHintTextSchema, CHMHistoryType
from hints_common.battle.schemas.base import CommonHintContextModel, CommonHintPropsSchema, CommonHintPropsModel
if typing.TYPE_CHECKING:
    from dict2model.extensions.battle_type import BattleTypeModel

class GrinchEventHintTextModel(ClientHintTextModel):
    __slots__ = ('subtitleKey', '_subtitle')

    def __init__(self, raw, key, template, highlight, subtitleKey):
        super(GrinchEventHintTextModel, self).__init__(raw, key, template, highlight)
        self.subtitleKey = subtitleKey
        self._subtitle = self._createMessage(key=self.subtitleKey)

    @property
    def subtitle(self):
        return self._subtitle


class GrinchHintPropsModel(CommonHintPropsModel):
    __slots__ = ('showCountdown', 'icon')

    def __init__(self, name, scope, component, unique, priority, battleTypes, showCountdown, icon):
        super(GrinchHintPropsModel, self).__init__(name=name, scope=scope, component=component, unique=unique, priority=priority, battleTypes=battleTypes)
        self.showCountdown = showCountdown
        self.icon = icon


class GrinchHintPropsSchema(CommonHintPropsSchema[GrinchHintPropsModel]):

    def __init__(self):
        super(GrinchHintPropsSchema, self).__init__(modelClass=GrinchHintPropsModel)
        self._fields['showCountdown'] = fields.Boolean(required=False, default=True)
        self._fields['icon'] = fields.String(required=False, default='')


class GrinchEventHintTextSchema(ClientHintTextSchema[GrinchEventHintTextModel]):

    def __init__(self):
        super(GrinchEventHintTextSchema, self).__init__(checkUnknown=True, modelClass=GrinchEventHintTextModel)
        self._fields['subtitleKey'] = fields.String(required=False, default='')


class GrinchEventHintModel(ClientHintModel[GrinchHintPropsModel, GrinchEventHintTextModel, CHMVisualType, CHMSoundType, CHMLifecycleType, CommonHintContextModel, CHMHistoryType]):
    pass


hintPropsSchema = GrinchHintPropsSchema()
hintTextSchema = GrinchEventHintTextSchema()
hintSchema = ClientHintSchema[GrinchEventHintModel](propsSchema=hintPropsSchema, textSchema=hintTextSchema, contextSchema=CommonHintContextModel, modelClass=GrinchEventHintModel)
