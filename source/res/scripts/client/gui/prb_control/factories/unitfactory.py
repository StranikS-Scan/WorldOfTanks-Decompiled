# Embedded file name: scripts/client/gui/prb_control/factories/UnitFactory.py
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import prb_control
from gui.prb_control.context.unit_ctx import LeaveUnitCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional.unit import NoUnitFunctional, UnitEntry, UnitIntro
from gui.prb_control.functional.unit import IntroFunctional, UnitFunctional
from gui.prb_control.items import PlayerDecorator, FunctionalState
from gui.prb_control.items.unit_items import SupportedRosterSettings, DynamicRosterSettings
from gui.prb_control.settings import FUNCTIONAL_EXIT, PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE, UNIT_MODE_FLAGS

class UnitFactory(ControlFactory):

    def createEntry(self, ctx):
        if not ctx.getRequestType():
            entry = UnitIntro()
        else:
            entry = UnitEntry()
        return entry

    def createFunctional(self, dispatcher, ctx):
        unitMrg = prb_control.getClientUnitMgr()
        if unitMrg.id and unitMrg.unitIdx:
            unit = prb_control.getUnit(unitMrg.unitIdx, safe=True)
            prbType = PREBATTLE_TYPE.UNIT
            if unit.isSortie():
                prbType = PREBATTLE_TYPE.SORTIE
            if unit:
                unitFunctional = UnitFunctional(prbType, DynamicRosterSettings(unit))
                for listener in dispatcher._globalListeners:
                    unitFunctional.addListener(listener())

            else:
                LOG_ERROR('Unit is not found in unit manager', unitMrg.unitIdx, unitMrg.units)
                unitMrg.leave()
                unitFunctional = NoUnitFunctional()
        else:
            func = dispatcher.getUnitFunctional()
            params = ctx.getCreateParams()
            prbType = params.get('prbType')
            modeFlags = params.get('modeFlags', UNIT_MODE_FLAGS.UNDEFINED)
            toIntro = func and func.getExit() == FUNCTIONAL_EXIT.INTRO_UNIT
            if toIntro or prbType is not None:
                if prbType is None:
                    prbType = func.getPrbType()
                rosterSettings = SupportedRosterSettings.last(prbType)
                unitFunctional = IntroFunctional(prbType, modeFlags, rosterSettings)
                for listener in dispatcher._globalListeners:
                    unitFunctional.addListener(listener())

            else:
                unitFunctional = NoUnitFunctional()
        return unitFunctional

    def createPlayerInfo(self, functional):
        info = functional.getPlayerInfo(unitIdx=functional.getUnitIdx())
        return PlayerDecorator(info.isCreator(), info.isReady)

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.UNIT, functional.getPrbType(), True, isinstance(functional, IntroFunctional))

    def createLeaveCtx(self):
        return LeaveUnitCtx(waitingID='prebattle/leave')

    def getLeaveCtxByAction(self, action):
        ctx = None
        if action in [PREBATTLE_ACTION_NAME.UNIT_LEAVE, PREBATTLE_ACTION_NAME.SORTIE_LEAVE]:
            ctx = self.createLeaveCtx()
        return ctx

    def getOpenListCtxByAction(self, action):
        return None
