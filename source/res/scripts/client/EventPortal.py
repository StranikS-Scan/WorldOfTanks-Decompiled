# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventPortal.py
import logging
from ClientSelectableCameraObject import ClientSelectableCameraObject
from helpers import dependency
from shared_utils import nextTick
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
            nextTick(self.gameEventCtrl.doLeaveEventPrb)()
        else:
            nextTick(self.gameEventCtrl.doSelectEventPrb)()

    @property
    def isMouseSelectionLocked(self):
        return False

    def _getCollisionModelsPrereqs(self):
        if self.outlineModelName:
            collisionModels = ((0, self.outlineModelName),)
            return collisionModels
        return super(EventPortal, self)._getCollisionModelsPrereqs()
