# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/squad/actions_handler.py
import account_helpers
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from th_async import th_async, th_await
from BWUtil import AsyncReturn
from portal.gui.shared.event_dispatcher import showPortalBattleQueueView
from portal.skeletons.portal_event_controller import IPortalEventController

class PortalSquadActionsHandler(SquadActionsHandler):
    __portalEventController = dependency.descriptor(IPortalEventController)

    def executeInit(self, ctx):
        result = super(PortalSquadActionsHandler, self).executeInit(ctx)
        self.setPlayerInfoChanged()
        return result

    def executeFini(self):
        super(PortalSquadActionsHandler, self).executeFini()
        self.__portalEventController.setMaxAvailableComplexityLevel(None)
        return

    def setUnitChanged(self, loadHangar=False):
        flags = self._entity.getFlags()
        if self._entity.getPlayerInfo().isReady and flags.isInQueue():
            _, unit = self._entity.getUnit()
            pInfo = self._entity.getPlayerInfo()
            vInfos = unit.getMemberVehicles(pInfo.dbID)
            if vInfos is not None:
                g_currentVehicle.selectVehicle(vInfos[0].vehInvID)
            self.__showBattleQueueGUI()
        elif loadHangar:
            g_eventDispatcher.loadHangar()
        return

    def setPlayerInfoChanged(self, pInfo=None):
        if pInfo and pInfo.dbID != account_helpers.getAccountDatabaseID():
            return
        else:
            extraData = pInfo.extraData if pInfo else {}
            if not pInfo:
                _, unit = self._entity.getUnit()
                player = unit.getPlayer(dbID=account_helpers.getAccountDatabaseID())
                extraData = player.get('extraData', {})
            portalEnqueueData = extraData.get('portalEnqueueData', {})
            battleLevel = portalEnqueueData.get('battleLevel')
            if battleLevel is not None:
                self.__portalEventController.onSquadBattleLevelChanged(battleLevel)
            maxAvailableBattleLevel = portalEnqueueData.get('maxAvailableBattleLevel')
            if maxAvailableBattleLevel is not None:
                self.__portalEventController.setMaxAvailableComplexityLevel(maxAvailableBattleLevel)
            return

    @th_async
    def _validateUnitState(self, entity, checkAmmo=False):
        result = yield th_await(super(PortalSquadActionsHandler, self)._validateUnitState(entity, checkAmmo=checkAmmo))
        if not result:
            raise AsyncReturn(result)
        raise AsyncReturn(True)

    def __showBattleQueueGUI(self):
        showPortalBattleQueueView()
