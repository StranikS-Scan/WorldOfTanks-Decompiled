# Embedded file name: scripts/client/gui/prb_control/factories/UnitFactory.py
from constants import PREBATTLE_TYPE, FALLOUT_BATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.context.unit_ctx import LeaveUnitCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional import unit
from gui.prb_control.items import PlayerDecorator, FunctionalState, unit_items
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.prb_control.settings import FUNCTIONAL_FLAG
__all__ = ('UnitFactory',)
_PAN = PREBATTLE_ACTION_NAME
_SUPPORTED_ENTRY_BY_ACTION = {_PAN.SQUAD: (unit.SquadEntry, None),
 _PAN.UNIT: (unit.UnitIntro, (PREBATTLE_TYPE.UNIT,)),
 _PAN.FORT: (unit.UnitIntro, (PREBATTLE_TYPE.SORTIE,))}
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.SQUAD: unit.SquadEntry,
 PREBATTLE_TYPE.UNIT: unit.UnitEntry,
 PREBATTLE_TYPE.SORTIE: unit.UnitEntry,
 PREBATTLE_TYPE.FORT_BATTLE: unit.FortBattleEntry,
 PREBATTLE_TYPE.CLUBS: unit.ClubBattleEntry}

class UnitFactory(ControlFactory):

    def createEntry(self, ctx):
        if not ctx.getRequestType():
            entry = unit.UnitIntro(ctx.getEntityType())
        else:
            clazz = _SUPPORTED_ENTRY_BY_TYPE.get(ctx.getEntityType())
            if clazz is not None:
                entry = clazz()
            else:
                entry = None
                LOG_ERROR('Prebattle type is not supported', ctx)
        return entry

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createFunctional(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.UNIT:
            created = self._createByAccountState(ctx)
        else:
            created = self._createByFlags(ctx)
        return created

    def createPlayerInfo(self, functional):
        info = functional.getPlayerInfo(unitIdx=functional.getUnitIdx())
        return PlayerDecorator(info.isCreator(), info.isReady)

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.UNIT, functional.getEntityType(), True, functional.hasLockedState(), isinstance(functional, unit.IntroFunctional), functional.getFlags(), functional.getExtra())

    def createLeaveCtx(self, flags = FUNCTIONAL_FLAG.UNDEFINED):
        return LeaveUnitCtx(waitingID='prebattle/leave', flags=flags)

    def _createByAccountState(self, ctx):
        unitMrg = prb_getters.getClientUnitMgr()
        if unitMrg is None:
            return self._createNoUnitFunctional(ctx)
        else:
            if unitMrg.id and unitMrg.unitIdx:
                entity = prb_getters.getUnit(unitMrg.unitIdx, safe=True)
                if entity:
                    flags = FUNCTIONAL_FLAG.UNIT
                    if ctx.hasFlags(FUNCTIONAL_FLAG.UNIT_INTRO) and entity.getPrebattleType() == ctx.getEntityType():
                        flags |= FUNCTIONAL_FLAG.SWITCH
                    if entity.isSquad():
                        flags |= FUNCTIONAL_FLAG.SQUAD
                        extra = entity.getExtra()
                        if extra is not None and extra.eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
                            flags |= FUNCTIONAL_FLAG.EVENT_SQUAD
                    ctx.removeFlags(FUNCTIONAL_FLAG.UNIT_BITMASK | FUNCTIONAL_FLAG.ACTIONS_BITMASK)
                    ctx.addFlags(flags)
                    created = unit.UnitFunctional(entity.getPrebattleType(), unit_items.DynamicRosterSettings(entity), flags=flags)
                else:
                    LOG_ERROR('Unit is not found in unit manager', unitMrg.unitIdx, unitMrg.units)
                    unitMrg.leave()
                    created = self._createNoUnitFunctional(ctx)
            else:
                created = self._createByPrbType(ctx)
            return created

    def _createByFlags(self, ctx):
        if not ctx.hasFlags(FUNCTIONAL_FLAG.UNIT):
            created = self._createByAccountState(ctx)
        else:
            created = self._createNoUnitFunctional(ctx)
        return created

    def _createByPrbType(self, ctx):
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.UNIT:
            return self._createNoUnitFunctional(ctx)
        prbType = ctx.getEntityType()
        if prbType:
            ctx.removeFlags(FUNCTIONAL_FLAG.UNIT_BITMASK)
            ctx.addFlags(FUNCTIONAL_FLAG.UNIT_INTRO)
            created = unit.IntroFunctional(prbType, ctx.getFlags() & FUNCTIONAL_FLAG.ACTIONS_BITMASK, unit_items.SupportedRosterSettings.last(prbType))
        else:
            created = self._createNoUnitFunctional(ctx)
        return created

    @staticmethod
    def _createNoUnitFunctional(ctx):
        if ctx.hasFlags(FUNCTIONAL_FLAG.LEAVE_ENTITY) and ctx.hasFlags(FUNCTIONAL_FLAG.UNIT_INTRO):
            return
        else:
            if not ctx.hasFlags(FUNCTIONAL_FLAG.NO_UNIT):
                ctx.removeFlags(FUNCTIONAL_FLAG.UNIT_BITMASK)
                ctx.addFlags(FUNCTIONAL_FLAG.NO_UNIT)
                created = unit.NoUnitFunctional()
            else:
                created = None
            return created
