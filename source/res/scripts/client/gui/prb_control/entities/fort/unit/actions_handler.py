# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/actions_handler.py
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.unit.actions_handler import UnitActionsHandler
from gui.prb_control.settings import FUNCTIONAL_FLAG

class FortActionsHandler(UnitActionsHandler):
    """
    Fort actions handler class
    """

    def showGUI(self):
        g_eventDispatcher.showFortWindow()

    def executeInit(self, ctx):
        prbType = self._entity.getEntityType()
        flags = self._entity.getFlags()
        g_eventDispatcher.loadFort(prbType)
        if flags.isInIdle():
            g_eventDispatcher.setUnitProgressInCarousel(prbType, True)
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def _canDoAutoSearch(self, unit, stats):
        return False
