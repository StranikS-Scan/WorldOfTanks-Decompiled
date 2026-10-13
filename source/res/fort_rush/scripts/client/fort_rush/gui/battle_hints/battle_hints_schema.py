# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_hints/battle_hints_schema.py
from __future__ import absolute_import
import typing
from dict2model import fields
from hints.battle.schemas.base import ClientHintTextModel, ClientHintModel, CHMLifecycleType, CHMVisualType, CHMSoundType, ClientHintSchema, ClientHintTextSchema, CHMHistoryType
from hints_common.battle.schemas.base import CommonHintContextModel, CommonHintPropsSchema, CommonHintPropsModel
if typing.TYPE_CHECKING:
    from dict2model.extensions.battle_type import BattleTypeModel

class FortRushHintTextModel(ClientHintTextModel):
    __slots__ = ('descriptionKey', '_description')

    def __init__(self, raw, key, template, highlight, descriptionKey):
        super(FortRushHintTextModel, self).__init__(raw, key, template, highlight)
        self.descriptionKey = descriptionKey
        self._description = self._createMessage(key=self.descriptionKey)

    @property
    def description(self):
        return self._description


class FortRushHintPropsModel(CommonHintPropsModel):
    __slots__ = ('showCountdown',)

    def __init__(self, name, scope, component, unique, priority, skipOverlay, battleTypes, showCountdown):
        super(FortRushHintPropsModel, self).__init__(name=name, scope=scope, component=component, unique=unique, priority=priority, skipOverlay=skipOverlay, battleTypes=battleTypes)
        self.showCountdown = showCountdown


class FortRushHintPropsSchema(CommonHintPropsSchema[FortRushHintPropsModel]):

    def __init__(self):
        super(FortRushHintPropsSchema, self).__init__(modelClass=FortRushHintPropsModel)
        self._fields['showCountdown'] = fields.Boolean(required=False, default=True)


class FortRushHintTextSchema(ClientHintTextSchema[FortRushHintTextModel]):

    def __init__(self):
        super(FortRushHintTextSchema, self).__init__(checkUnknown=True, modelClass=FortRushHintTextModel)
        self._fields['descriptionKey'] = fields.String(required=False, default='')


class FortRushHintModel(ClientHintModel[FortRushHintPropsModel, FortRushHintTextModel, CHMVisualType, CHMSoundType, CHMLifecycleType, CommonHintContextModel, CHMHistoryType]):
    pass


hintPropsSchema = FortRushHintPropsSchema()
hintTextSchema = FortRushHintTextSchema()
hintSchema = ClientHintSchema[FortRushHintModel](propsSchema=hintPropsSchema, textSchema=hintTextSchema, contextSchema=CommonHintContextModel, modelClass=FortRushHintModel)
