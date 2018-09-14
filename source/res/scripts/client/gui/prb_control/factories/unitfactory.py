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
from gui.prb_control.entities.fallout.squad.entity import FalloutSquadEntity, FalloutSquadEntryPoint
from gui.prb_control.entities.fort.unit.fort_battle.entity import FortBattleBrowserEntity, FortBattleEntity
from gui.prb_control.entities.fort.unit.fort_battle.entity import FortBattleBrowserEntryPoint, FortBattleEntryPoint
from gui.prb_control.entities.fort.unit.entity import FortIntroEntity, FortIntroEntryPoint
from gui.prb_control.entities.fort.unit.sortie.entity import SortieBrowserEntity, SortieEntity
from gui.prb_control.entities.fort.unit.sortie.entity import SortieBrowserEntryPoint, SortieEntryPoint
from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity, StrongholdEntryPoint, StrongholdBrowserEntryPoint, StrongholdBrowserEntity
from gui.prb_control.entities.random.squad.entity import RandomSquadEntity, RandomSquadEntryPoint
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
__all__ = ('UnitFactory',)
_SUPPORTED_ENTRY_BY_ACTION = {PREBATTLE_ACTION_NAME.SQUAD: RandomSquadEntryPoint,
 PREBATTLE_ACTION_NAME.EVENT_SQUAD: EventBattleSquadEntryPoint,
 PREBATTLE_ACTION_NAME.E_SPORT: ESportIntroEntry,
 PREBATTLE_ACTION_NAME.PUBLICS_LIST: PublicBrowserEntryPoint,
 PREBATTLE_ACTION_NAME.FORT: FortIntroEntryPoint,
 PREBATTLE_ACTION_NAME.SORTIES_LIST: SortieBrowserEntryPoint,
 PREBATTLE_ACTION_NAME.FORT_BATTLES_LIST: FortBattleBrowserEntryPoint,
 PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST: StrongholdBrowserEntryPoint}
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.SQUAD: RandomSquadEntryPoint,
 PREBATTLE_TYPE.EVENT: EventBattleSquadEntryPoint,
 PREBATTLE_TYPE.FALLOUT: FalloutSquadEntryPoint,
 PREBATTLE_TYPE.UNIT: PublicEntryPoint,
 PREBATTLE_TYPE.SORTIE: SortieEntryPoint,
 PREBATTLE_TYPE.FORT_BATTLE: FortBattleEntryPoint,
 PREBATTLE_TYPE.EXTERNAL: StrongholdEntryPoint}
_SUPPORTED_INTRO_BY_TYPE = {PREBATTLE_TYPE.E_SPORT_COMMON: ESportIntroEntity,
 PREBATTLE_TYPE.FORT_COMMON: FortIntroEntity}
_SUPPORTED_BROWSER_BY_TYPE = {PREBATTLE_TYPE.UNIT: PublicBrowserEntity,
 PREBATTLE_TYPE.SORTIE: SortieBrowserEntity,
 PREBATTLE_TYPE.FORT_BATTLE: FortBattleBrowserEntity,
 PREBATTLE_TYPE.EXTERNAL: StrongholdBrowserEntity}
_SUPPORTED_UNIT_BY_TYPE = {PREBATTLE_TYPE.SQUAD: RandomSquadEntity,
 PREBATTLE_TYPE.EVENT: EventBattleSquadEntity,
 PREBATTLE_TYPE.FALLOUT: FalloutSquadEntity,
 PREBATTLE_TYPE.UNIT: PublicEntity,
 PREBATTLE_TYPE.SORTIE: SortieEntity,
 PREBATTLE_TYPE.FORT_BATTLE: FortBattleEntity,
 PREBATTLE_TYPE.EXTERNAL: StrongholdEntity}

class UnitFactory(ControlFactory):
    """
    Creates entry point, ctx or entity for unit control.
    """

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
        info = entity.getPlayerInfo(unitIdx=entity.getUnitIdx())
        return PlayerDecorator(info.isCommander(), info.isReady)

    def createStateEntity(self, entity):
        return FunctionalState(CTRL_ENTITY_TYPE.UNIT, entity.getEntityType(), True, entity.hasLockedState(), isinstance(entity, UnitIntroEntity), entity.getFlags(), entity.getFunctionalFlags(), entity.getRosterType())

    def createLeaveCtx(self, flags=FUNCTIONAL_FLAG.UNDEFINED, entityType=0):
        return LeaveUnitCtx(waitingID='prebattle/leave', flags=flags, entityType=entityType)

    def __createByAccountState(self, ctx):
        """
        Tries to create entity by current account state.
        Args:
            ctx: creation request context.
        
        Returns:
            new prebattle unit entity
        """
        unitMrg = prb_getters.getClientUnitMgr()
        if unitMrg is None:
            return
        else:
            if unitMrg.id and unitMrg.unitIdx:
                entity = prb_getters.getUnit(unitMrg.unitIdx, safe=True)
                if entity:
                    return self._createEntityByType(entity.getPrebattleType(), _SUPPORTED_UNIT_BY_TYPE)
                else:
                    LOG_ERROR('Unit is not found in unit manager', unitMrg.unitIdx, unitMrg.units)
                    unitMrg.leave()
                    return
            return self.__createByPrbType(ctx)

    def __createByFlags(self, ctx):
        """
        Tries to create entity by context flags.
        Args:
            ctx: creation request context.
        
        Returns:
            new prebattle unit entity
        """
        return self.__createByAccountState(ctx) if not ctx.hasFlags(FUNCTIONAL_FLAG.UNIT) else None

    def __createByPrbType(self, ctx):
        """
        Tries to create entity by prebattle type.
        Args:
            ctx: creation request context.
        
        Returns:
            new prebattle unit entity
        """
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.UNIT:
            return None
        else:
            prbType = ctx.getEntityType()
            if prbType in _SUPPORTED_INTRO_BY_TYPE:
                return self._createEntityByType(prbType, _SUPPORTED_INTRO_BY_TYPE)
            return self._createEntityByType(prbType, _SUPPORTED_BROWSER_BY_TYPE) if prbType in _SUPPORTED_BROWSER_BY_TYPE and ctx.hasFlags(FUNCTIONAL_FLAG.UNIT_BROWSER) else None
