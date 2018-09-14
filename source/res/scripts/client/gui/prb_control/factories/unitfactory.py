# Embedded file name: scripts/client/gui/prb_control/factories/UnitFactory.py
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import prb_control
from gui.prb_control.context.unit_ctx import LeaveUnitCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional.unit import NoUnitFunctional, UnitEntry, UnitIntro, FortBattleEntry, ClubBattleEntry
from gui.prb_control.functional.unit import IntroFunctional, UnitFunctional
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.items.unit_items import SupportedRosterSettings, DynamicRosterSettings
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE, UNIT_MODE_FLAGS, FUNCTIONAL_EXIT
_PAN = PREBATTLE_ACTION_NAME
_SUPPORTED_ENTRY_BY_ACTION = {_PAN.UNIT: (UnitIntro, (PREBATTLE_TYPE.UNIT,)),
 _PAN.FORT: (UnitIntro, (PREBATTLE_TYPE.SORTIE,))}
_SUPPORTED_ENTRY_BY_TYPE = {PREBATTLE_TYPE.UNIT: UnitEntry,
 PREBATTLE_TYPE.SORTIE: UnitEntry,
 PREBATTLE_TYPE.FORT_BATTLE: FortBattleEntry,
 PREBATTLE_TYPE.CLUBS: ClubBattleEntry}

class UnitFactory(ControlFactory):

    def createEntry(self, ctx):
        if not ctx.getRequestType():
            entry = UnitIntro(ctx.getPrbType())
        else:
            clazz = _SUPPORTED_ENTRY_BY_TYPE.get(ctx.getPrbType())
            if clazz is not None:
                entry = clazz()
            else:
                entry = None
                LOG_ERROR('Prebattle type is not supported', ctx)
        return entry

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createFunctional(self, dispatcher, ctx):
        unitMrg = prb_control.getClientUnitMgr()
        if unitMrg.id and unitMrg.unitIdx:
            unit = prb_control.getUnit(unitMrg.unitIdx, safe=True)
            if unit:
                unitFunctional = UnitFunctional(unit.getPrebattleType(), DynamicRosterSettings(unit))
                for listener in dispatcher._globalListeners:
                    unitFunctional.addListener(listener())

            else:
                LOG_ERROR('Unit is not found in unit manager', unitMrg.unitIdx, unitMrg.units)
                unitMrg.leave()
                unitFunctional = NoUnitFunctional()
        else:
            prbType = ctx.getPrbType()
            if prbType:
                unitFunctional = IntroFunctional(prbType, ctx.getCreateParams().get('modeFlags', UNIT_MODE_FLAGS.UNDEFINED), SupportedRosterSettings.last(prbType))
                for listener in dispatcher._globalListeners:
                    unitFunctional.addListener(listener())

            else:
                unitFunctional = NoUnitFunctional()
        return unitFunctional

    def createPlayerInfo(self, functional):
        info = functional.getPlayerInfo(unitIdx=functional.getUnitIdx())
        return PlayerDecorator(info.isCreator(), info.isReady)

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.UNIT, functional.getPrbType(), True, functional.hasLockedState(), isinstance(functional, IntroFunctional), functional.getState())

    def createLeaveCtx(self, funcExit = FUNCTIONAL_EXIT.NO_FUNC):
        return LeaveUnitCtx(waitingID='prebattle/leave', funcExit=funcExit)

    def getLeaveCtxByAction(self, action):
        ctx = None
        if action in (PREBATTLE_ACTION_NAME.UNIT_LEAVE, PREBATTLE_ACTION_NAME.FORT_LEAVE):
            ctx = self.createLeaveCtx()
        return ctx
