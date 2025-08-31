# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventPortal.py
import logging
import CGF
from ClientSelectableCameraObject import ClientSelectableCameraObject
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from skeletons.gui.game_control import IWhiteTigerController
_logger = logging.getLogger(__name__)

class EventPortal(ClientSelectableCameraObject):
    gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    def select(self):
        if not self.gameEventCtrl.isAvailable():
            return
        self.gameEventCtrl.doSelectEventPrb()

    def onEnterWorld(self, prereqs):
        self.setEnable(True)
        super(EventPortal, self).onEnterWorld(prereqs)

    def onLeaveWorld(self):
        self.setEnable(False)
        super(EventPortal, self).onLeaveWorld()

    def onMouseClick(self):
        if not self.gameEventCtrl.isAvailable():
            return
        if self.isMouseSelectionLocked:
            _logger.info('Click operation for portal is forbidden due to cooldown!')
            return
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.EVENT_PORTAL_SELECTED), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.gameEventCtrl.isEventPrbActive():
            self.gameEventCtrl.doLeaveEventPrb()
        else:
            self.gameEventCtrl.doSelectEventPrb()

    def setHighlight(self, show, fallback=False):
        super(EventPortal, self).setHighlight(show)
        if fallback:
            return
        from EventVehicle import EventVehicle
        query = CGF.Query(self.spaceID, EventVehicle)
        if not query.empty():
            for vehicle in query.values():
                vehicle.setHighlight(show, fallback=True)

    @property
    def isMouseSelectionLocked(self):
        return False

    def _getCollisionModelsPrereqs(self):
        if self.outlineModelName:
            collisionModels = ((0, self.outlineModelName),)
            return collisionModels
        return super(EventPortal, self)._getCollisionModelsPrereqs()
