# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventPortal.py
import logging
import BigWorld
import CGF
from ClientSelectableCameraObject import ClientSelectableCameraObject
from frameworks.wulf import WindowLayer
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from shared_utils import safeCancelCallback
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)

class _Lock(object):
    _LOCK_DELAY = 0.3

    def __init__(self):
        super(_Lock, self).__init__()
        self.__topSubViewDict = {}
        self.__currentCbId = None
        return

    def start(self):
        super(_Lock, self).__init__()
        g_eventDispatcher.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer

    def destroy(self):
        dictKeys = self.__topSubViewDict.keys()
        for alias in dictKeys:
            self.__clearTopSubView(alias)

        self.__clearCooldown()
        g_eventDispatcher.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer

    @property
    def isLocked(self):
        return self.__currentCbId is not None

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.layer == WindowLayer.TOP_SUB_VIEW:
            pyEntity.onDispose += self.__onTopSubViewDestroyed
            alias = pyEntity.alias
            self.__topSubViewDict[alias] = pyEntity
            self.__clearCooldown()

    def __onTopSubViewDestroyed(self, view):
        if view.alias in self.__topSubViewDict:
            self.__clearTopSubView(view.alias)
        else:
            _logger.warning('Something went wrong, could not find registered alias in the dict')
        if not bool(self.__topSubViewDict):
            self.__currentCbId = BigWorld.callback(self._LOCK_DELAY, self.__onCbComplete)

    def __clearTopSubView(self, alias):
        self.__topSubViewDict[alias].onDispose -= self.__onTopSubViewDestroyed
        del self.__topSubViewDict[alias]

    def __clearCooldown(self):
        if self.__currentCbId is not None:
            safeCancelCallback(self.__currentCbId)
            self.__currentCbId = None
        return

    def __onCbComplete(self):
        self.__currentCbId = None
        return


class EventPortal(ClientSelectableCameraObject):
    gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        super(EventPortal, self).__init__()
        self.__lock = _Lock()

    def select(self):
        self.gameEventCtrl.doSelectEventPrb()

    def onEnterWorld(self, prereqs):
        self.__lock.start()
        super(EventPortal, self).onEnterWorld(prereqs)

    def onLeaveWorld(self):
        self.__lock.destroy()
        self.__lock = None
        self.setEnable(False)
        super(EventPortal, self).onLeaveWorld()
        return

    def onMouseClick(self):
        if self.isMouseSelectionLocked:
            _logger.info('Click operation for portal is forbidden due to cooldown!')
            return
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.EVENT_PORTAL_SELECTED), scope=EVENT_BUS_SCOPE.LOBBY)
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
        return self.__lock.isLocked

    def _getCollisionModelsPrereqs(self):
        if self.outlineModelName:
            collisionModels = ((0, self.outlineModelName),)
            return collisionModels
        return super(EventPortal, self)._getCollisionModelsPrereqs()
