# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/UnitFactory.py
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.entities.base.unit.ctx import LeaveUnitCtx
from gui.prb_control.entities.base.unit.entity import UnitIntroEntity
from gui.prb_control.entities.e_sport.unit.entity import ESportIntroEntity, ESportIntroEntry
from gui.prb_control.entities.e_sport.unit.public.entity import PublicBrowserEntity, PublicEntity
from gui.prb_control.entities.e_sport.unit.public.entity import PublicBrowserEntryPoint, PublicEntryPoint
from gui.prb_control.entities.event.squad.entity import EventBattleSquadEntity, EventBattleSquadEntryPoint
from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity, StrongholdEntryPoint, StrongholdBrowserEntryPoint, StrongholdBrowserEntity
from gui.prb_control.entities.random.squad.entity import RandomSquadEntity, RandomSquadEntryPoint
from gui.prb_control.entities.epic.squad.entity import EpicSquadEntity, EpicSquadEntryPoint
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
__all__ = ('UnitFactory',)
_SUPPORTED_ENTRY_BY_ACTION = {PREBATTLE_ACTION_NAME.SQUAD: RandomSquadEntryPoint,
 PREBATTLE_ACTION_NAME.EVENT_SQUAD: EventBattleSquadEntryPoint,
 PREBATTLE_ACTION_NAME.E_SPORT: ESportIntroEntry,
 PREBATTLE_ACTION_NAME.PUBLICS_LIST: PublicBrowserEntryPoint,
 PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST: StrongholdBrowserEntryPoint}
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.SQUAD: RandomSquadEntryPoint,
 PREBATTLE_TYPE.EVENT: EventBattleSquadEntryPoint,
 PREBATTLE_TYPE.EPIC: EpicSquadEntryPoint,
 PREBATTLE_TYPE.UNIT: PublicEntryPoint,
 PREBATTLE_TYPE.EXTERNAL: StrongholdEntryPoint}
_SUPPORTED_INTRO_BY_TYPE = {PREBATTLE_TYPE.E_SPORT_COMMON: ESportIntroEntity}
_SUPPORTED_BROWSER_BY_TYPE = {PREBATTLE_TYPE.UNIT: PublicBrowserEntity,
 PREBATTLE_TYPE.EXTERNAL: StrongholdBrowserEntity}
_SUPPORTED_UNIT_BY_TYPE = {PREBATTLE_TYPE.SQUAD: RandomSquadEntity,
 PREBATTLE_TYPE.EVENT: EventBattleSquadEntity,
 PREBATTLE_TYPE.EPIC: EpicSquadEntity,
 PREBATTLE_TYPE.UNIT: PublicEntity,
 PREBATTLE_TYPE.EXTERNAL: StrongholdEntity}

class UnitFactory(ControlFactory):

    def createEntry(self, ctx):
        return self._createEntryByType(ctx.getEntityType(), _SUPPORTED_ENTRY_BY_TYPE)

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createEntity(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.UNIT:
            created = self.__createByAccountState(ctx)
        else:
            created = self.__createByFlags(ctx)
        return created

    def createPlayerInfo(self, entity):
        info = entity.getPlayerInfo(unitMgrID=entity.getID())
        return PlayerDecorator(info.isCommander(), info.isReady)

    def createStateEntity(self, entity):
        return FunctionalState(CTRL_ENTITY_TYPE.UNIT, entity.getEntityType(), True, entity.hasLockedState(), isinstance(entity, UnitIntroEntity), entity.getFlags(), entity.getFunctionalFlags(), entity.getRosterType())

    def createLeaveCtx(self, flags=FUNCTIONAL_FLAG.UNDEFINED, entityType=0):
        return LeaveUnitCtx(waitingID='prebattle/leave', flags=flags, entityType=entityType)

    def __createByAccountState(self, ctx):
        unitMrg = prb_getters.getClientUnitMgr()
        if unitMrg is None:
            return
        elif unitMrg.id:
            entity = prb_getters.getUnit(safe=True)
            if entity is None:
                LOG_ERROR('Unit is not found in unit manager', unitMrg.id, unitMrg.unit)
                unitMrg.leave()
                return
            return self._createEntityByType(entity.getPrebattleType(), _SUPPORTED_UNIT_BY_TYPE)
        else:
            return self.__createByPrbType(ctx)

    def __createByFlags(self, ctx):
        return self.__createByAccountState(ctx) if not ctx.hasFlags(FUNCTIONAL_FLAG.UNIT) else None

    def __createByPrbType(self, ctx):
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.UNIT:
            return None
        else:
            prbType = ctx.getEntityType()
            if prbType in _SUPPORTED_INTRO_BY_TYPE:
                return self._createEntityByType(prbType, _SUPPORTED_INTRO_BY_TYPE)
            return self._createEntityByType(prbType, _SUPPORTED_BROWSER_BY_TYPE) if prbType in _SUPPORTED_BROWSER_BY_TYPE and ctx.hasFlags(FUNCTIONAL_FLAG.UNIT_BROWSER) else None
