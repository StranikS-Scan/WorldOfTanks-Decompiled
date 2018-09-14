# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/sortie/entity.py
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.entities.fort.unit.entity import FortEntity, FortBrowserEntity, FortBrowserEntryPoint, FortEntryPoint
from gui.prb_control.entities.fort.unit.sortie.actions_validator import SortieActionsValidator
from gui.prb_control.entities.fort.unit.sortie.scheduler import SortiesScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.fortifications import getClientFortMgr

class SortieBrowserEntryPoint(FortBrowserEntryPoint):
    """
    Sortie list entry point
    """

    def __init__(self):
        super(SortieBrowserEntryPoint, self).__init__(PREBATTLE_TYPE.SORTIE)


class SortieEntryPoint(FortEntryPoint):
    """
    Sortie entry point
    """

    def create(self, ctx, callback=None):
        if not prb_getters.hasModalEntity() or ctx.isForced():
            fortMgr = getClientFortMgr()
            if fortMgr:
                ctx.startProcessing(callback=callback)
                fortMgr.createSortie(ctx.getDivisionLevel())
            else:
                LOG_ERROR('Fort provider is not defined')
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return


class SortieBrowserEntity(FortBrowserEntity):
    """
    Sortie list entity
    """

    def __init__(self):
        super(SortieBrowserEntity, self).__init__(PREBATTLE_TYPE.SORTIE)

    def fini(self, ctx=None, woEvents=False):
        if self.fortCtrl:
            self.fortCtrl.removeSortiesCache()
        return super(SortieBrowserEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getBrowser(self):
        return self.fortCtrl.getSortiesCache() if self.fortCtrl else None

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.FORT:
            g_eventDispatcher.showFortWindow()
            return SelectResult(True)
        return super(SortieBrowserEntity, self).doSelectAction(action)


class SortieEntity(FortEntity):
    """
    Sortie entity
    """

    def __init__(self):
        super(SortieEntity, self).__init__(PREBATTLE_TYPE.SORTIE)
        self.__isLegionary = False

    def init(self, ctx=None):
        result = super(SortieEntity, self).init(ctx)
        self.__isLegionary = self.getPlayerInfo().isLegionary()
        return result

    def getQueueType(self):
        return QUEUE_TYPE.SORTIE

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.FORT:
            g_eventDispatcher.showFortWindow()
            return SelectResult(True)
        return super(SortieEntity, self).doSelectAction(action)

    def canKeepMode(self):
        return False if self.__isLegionary else super(SortieEntity, self).canKeepMode()

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(SortieEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.__isLegionary = self.getPlayerInfo().isLegionary()

    def _createActionsValidator(self):
        return SortieActionsValidator(self)

    def _createScheduler(self):
        return SortiesScheduler(self)
