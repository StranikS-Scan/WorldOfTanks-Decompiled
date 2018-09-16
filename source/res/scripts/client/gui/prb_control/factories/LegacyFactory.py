# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/LegacyFactory.py
from constants import PREBATTLE_TYPE
from gui.prb_control import prb_getters
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.entities.base.legacy.ctx import LeaveLegacyCtx
from gui.prb_control.entities.base.legacy.entity import LegacyIntroEntryPoint, LegacyInitEntity
from gui.prb_control.entities.base.legacy.entity import LegacyIntroEntity
from gui.prb_control.entities.battle_session.legacy.entity import BattleSessionEntryPoint
from gui.prb_control.entities.battle_session.legacy.entity import BattleSessionListEntryPoint, BattleSessionEntity
from gui.prb_control.entities.training.legacy.entity import TrainingEntryPoint, TrainingIntroEntryPoint
from gui.prb_control.entities.training.legacy.entity import TrainingEntity, TrainingIntroEntity
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
__all__ = ('LegacyFactory',)
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.TRAINING: TrainingEntryPoint,
 PREBATTLE_TYPE.TOURNAMENT: BattleSessionEntryPoint,
 PREBATTLE_TYPE.CLAN: BattleSessionEntryPoint}
_SUPPORTED_ENTRY_BY_ACTION = {PREBATTLE_ACTION_NAME.TRAININGS_LIST: TrainingIntroEntryPoint,
 PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST: BattleSessionListEntryPoint}
_SUPPORTED_ENTITY = {PREBATTLE_TYPE.TRAINING: TrainingEntity,
 PREBATTLE_TYPE.TOURNAMENT: BattleSessionEntity,
 PREBATTLE_TYPE.CLAN: BattleSessionEntity}
_SUPPORTED_INTRO_BY_TYPE = {PREBATTLE_TYPE.TRAINING: TrainingIntroEntity}

class LegacyFactory(ControlFactory):

    def createEntry(self, ctx):
        if not ctx.getRequestType():
            return LegacyIntroEntryPoint(FUNCTIONAL_FLAG.UNDEFINED, ctx.getEntityType())
        else:
            prbType = ctx.getEntityType()
            return _SUPPORTED_ENTRY_BY_TYPE[prbType]() if prbType in _SUPPORTED_ENTRY_BY_TYPE else None

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createEntity(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.LEGACY:
            created = self.__createByAccountState(ctx)
        else:
            created = self.__createByFlags(ctx)
        return created

    def createPlayerInfo(self, entity):
        info = entity.getPlayerInfo()
        return PlayerDecorator(info.isCreator, info.isReady())

    def createStateEntity(self, entity):
        return FunctionalState(CTRL_ENTITY_TYPE.LEGACY, entity.getEntityType(), True, entity.hasLockedState(), isinstance(entity, LegacyIntroEntity), funcFlags=entity.getFunctionalFlags())

    def createLeaveCtx(self, flags=FUNCTIONAL_FLAG.UNDEFINED, entityType=0):
        return LeaveLegacyCtx(waitingID='prebattle/leave', flags=flags, entityType=entityType)

    def __createByAccountState(self, ctx):
        clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            if prb_getters.isPrebattleSettingsReceived(prebattle=clientPrb):
                prbSettings = prb_getters.getPrebattleSettings(prebattle=clientPrb)
                prbType = prb_getters.getPrebattleType(settings=prbSettings)
                clazz = None
                if prbType in _SUPPORTED_ENTITY:
                    clazz = _SUPPORTED_ENTITY[prbType]
                if clazz:
                    return clazz(prbSettings)
            else:
                return LegacyInitEntity()
        return self.__createByPrbType(ctx)

    def __createByFlags(self, ctx):
        return self.__createByAccountState(ctx) if not ctx.hasFlags(FUNCTIONAL_FLAG.LEGACY) else None

    def __createByPrbType(self, ctx):
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.LEGACY:
            return None
        else:
            prbType = ctx.getEntityType()
            return self._createEntityByType(prbType, _SUPPORTED_INTRO_BY_TYPE) if prbType in _SUPPORTED_INTRO_BY_TYPE else None
