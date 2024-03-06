# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/extensions/battle_type.py
from __future__ import absolute_import
import typing
from constants import ARENA_BONUS_TYPE_NAMES, ARENA_GAMEPLAY_NAMES
from dict2model import models, validate
from dict2model.fields import UniCapList, String
from dict2model.schemas import Schema
if typing.TYPE_CHECKING:
    from dict2model.types import ValidatorsType
    from dict2model.fields import Field

class BattleTypeModel(models.Model):
    __slots__ = ('arenaBonusType', 'gameplayNames')

    def __init__(self, arenaBonusType, gameplayNames):
        super(BattleTypeModel, self).__init__()
        self.arenaBonusType = arenaBonusType
        self.gameplayNames = gameplayNames

    def _reprArgs(self):
        return 'arenaBonusType={}, gameplayNames={}'.format(self.arenaBonusType, self.gameplayNames)


_battleTypeSchema = Schema[BattleTypeModel](fields={'arenaBonusType': String(required=True, deserializedValidators=validate.OneOf(ARENA_BONUS_TYPE_NAMES)),
 'gameplayNames': UniCapList(fieldOrSchema=String(deserializedValidators=validate.OneOf(ARENA_GAMEPLAY_NAMES)), required=False, default=list)}, checkUnknown=True, modelClass=BattleTypeModel)

class BattleTypesModel(models.Model):
    __slots__ = ('battleTypes', '_gameplayByBattleType')

    def __init__(self, battleTypes):
        super(BattleTypesModel, self).__init__()
        self.battleTypes = battleTypes
        self._gameplayByBattleType = {ARENA_BONUS_TYPE_NAMES[bt.arenaBonusType]:set(bt.gameplayNames) for bt in self.battleTypes}

    def isSuitableForBattleType(self, arenaBonusType, gameplayName):
        if not self._gameplayByBattleType:
            return True
        if arenaBonusType not in self._gameplayByBattleType:
            return False
        gameplayNames = self._gameplayByBattleType[arenaBonusType]
        return False if gameplayNames and gameplayName not in gameplayNames else True

    def _reprArgs(self):
        return 'battleTypes={}'.format(self.battleTypes)


BattleTypesModelType = typing.TypeVar('BattleTypesModelType', bound=BattleTypesModel)

class BattleTypesSchema(Schema[BattleTypesModelType]):

    def __init__(self, fields, modelClass=BattleTypesModel, checkUnknown=True, serializedValidators=None, deserializedValidators=None):
        fields_ = {'battleTypes': UniCapList(fieldOrSchema=_battleTypeSchema, required=False, default=list)}
        fields_.update(fields)
        super(BattleTypesSchema, self).__init__(fields=fields_, modelClass=modelClass, checkUnknown=checkUnknown, serializedValidators=serializedValidators, deserializedValidators=deserializedValidators)
