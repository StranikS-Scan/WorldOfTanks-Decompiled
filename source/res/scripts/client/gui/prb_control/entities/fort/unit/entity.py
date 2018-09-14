# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/entity.py
from constants import PREBATTLE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.entity import UnitBrowserEntity, UnitIntroEntity, UnitEntity, UnitIntroEntryPoint, UnitBrowserEntryPoint, UnitEntryPoint
from gui.prb_control.entities.base.unit.listener import IUnitIntroListener
from gui.prb_control.entities.fort.unit.actions_handler import FortActionsHandler
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.shared.fortifications.fort_listener import fortCtrlProperty

class FortIntroEntryPoint(UnitIntroEntryPoint):
    """
    Fort intro entry point
    """

    def __init__(self):
        super(FortIntroEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT, PREBATTLE_TYPE.FORT_COMMON)


class FortBrowserEntryPoint(UnitBrowserEntryPoint):
    """
    Fort list base entry point
    """

    def __init__(self, prbType):
        super(FortBrowserEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT, prbType)


class FortEntryPoint(UnitEntryPoint):
    """
    Fort base entry point
    """

    def __init__(self, accountsToInvite=None):
        super(FortEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT, accountsToInvite)


class FortIntroEntity(UnitIntroEntity):
    """
    Fort intro entity
    """

    def __init__(self):
        super(FortIntroEntity, self).__init__(FUNCTIONAL_FLAG.FORT, {}, IUnitIntroListener, PREBATTLE_TYPE.FORT_COMMON)

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.FORT:
            self._showWindow()
            return SelectResult(True)
        return super(FortIntroEntity, self).doSelectAction(action)

    def _loadUnit(self):
        g_eventDispatcher.loadFort(self._prbType)

    def _unloadUnit(self):
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showFortWindow()


class FortBrowserEntity(UnitBrowserEntity):
    """
    Fort base browser entity
    """

    def __init__(self, prbType):
        super(FortBrowserEntity, self).__init__(FUNCTIONAL_FLAG.FORT, prbType)

    @fortCtrlProperty
    def fortCtrl(self):
        """
        Fort controller property getter
        """
        return None

    def getIntroType(self):
        return PREBATTLE_TYPE.FORT_COMMON

    def _getUnit(self, unitIdx=None):
        browser = self.getBrowser()
        return (unitIdx, browser.getUnitByIndex(unitIdx)) if browser is not None else super(FortBrowserEntity, self)._getUnit(unitIdx)

    def _loadUnit(self):
        g_eventDispatcher.loadFort(self._prbType)

    def _unloadUnit(self):
        g_eventDispatcher.loadHangar()
        g_eventDispatcher.removeUnitFromCarousel(self._prbType)

    def _showWindow(self):
        g_eventDispatcher.showFortWindow()


class FortEntity(UnitEntity):
    """
    Fort base entity
    """

    def __init__(self, prbType):
        super(FortEntity, self).__init__(FUNCTIONAL_FLAG.FORT, prbType)

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.FORT:
            g_eventDispatcher.showFortWindow()
            return SelectResult(True)
        return super(FortEntity, self).doSelectAction(action)

    def _createActionsHandler(self):
        return FortActionsHandler(self)
