# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spawn_ctrl.py
import logging
import BigWorld
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_battle
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, COUNTDOWN_STATE
from gui.battle_control.arena_info.interfaces import ISpawnController
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class ISpawnListener(object):

    def setSpawnPoints(self, points):
        pass

    def closeSpawnPoints(self):
        pass

    def updatePoint(self, vehicleId, pointId, prevPointId):
        pass

    def updateCloseTime(self, timeLeft, state):
        pass

    def onSelectPoint(self, pointId, entityID=None):
        pass


class SpawnController(ViewComponentsController, ISpawnController):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SpawnController, self).__init__()
        self.__ingameMenu = None
        self.__isSpawnPointsVisible = False
        self._pointsByVehicle = {}
        self.__closeTime = 0
        self.__cdState = COUNTDOWN_STATE.WAIT
        self.__notifier = self.__createNotifier()
        self._points = []
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPAWN_CTRL

    def iterSelectedPoints(self):
        for entityID, pointID in self._pointsByVehicle.iteritems():
            if pointID is not None:
                yield (entityID, pointID)

        return

    def isEntityAppliedToPoint(self, entityID):
        return entityID in self._pointsByVehicle

    def appliedPointsCount(self):
        return len(self._pointsByVehicle)

    def startControl(self, *args):
        pass

    def stopControl(self):
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__notifier.stopNotification()
        self.__removeListeners()
        self.__notifier.clear()
        self.__notifier = None
        self._pointsByVehicle = None
        self._points = None
        return

    def setViewComponents(self, *components):
        self._viewComponents.extend(components)
        self.__updateCloseTime()

    def showSpawnPoints(self, points):
        if not self.__isSpawnPointsVisible:
            if self._app:
                self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
            else:
                _logger.warning('App reference is still None!')
            self.__isSpawnPointsVisible = True
        for viewComponent in self._viewComponents:
            viewComponent.setSpawnPoints(points)

        self._points = points

    def setupCloseTime(self, closeTime):
        self.__closeTime = closeTime
        self.__cdState = COUNTDOWN_STATE.START
        self.__notifier.startNotification()

    def updateTeamSpawnKeyPoints(self, points):
        if not self.__isSpawnPointsVisible:
            return
        arenaDP = self._sessionProvider.getArenaDP()
        for point in points:
            pointId = point['guid']
            vehicleId = point['vehID']
            if vehicleId == arenaDP.getPlayerVehicleID():
                continue
            self._updateEntityPoint(vehicleId, pointId)

    def closeSpawnPoints(self):
        self.__closeSpawnPoints()

    def chooseSpawnKeyPoint(self, pointId):
        for viewComponent in self._viewComponents:
            viewComponent.onSelectPoint(pointId)

        self._invokeRemoteChooseMethod(pointId)

    def applySelection(self):
        self._invokeRemoteApplyMethod()
        self.__closeSpawnPoints()

    def addRuntimeView(self, view):
        if view in self._viewComponents:
            LOG_ERROR('View is already added! {}'.format(view))
        else:
            if self.__isSpawnPointsVisible:
                view.setSpawnPoints(self._points)
            self._viewComponents.append(view)

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)
        else:
            LOG_WARNING('View has not been found! {}'.format(view))

    @sf_battle
    def _app(self):
        return None

    def _updateEntityPoint(self, entryID, pointId):
        prevPoint = self._pointsByVehicle.get(entryID, None)
        isUpdated = False
        if prevPoint != pointId:
            for viewComponent in self._viewComponents:
                viewComponent.updatePoint(entryID, pointId, prevPoint)
                self._pointsByVehicle[entryID] = pointId
                isUpdated = True

        return isUpdated

    def _invokeRemoteChooseMethod(self, pointId, entityID=None):
        BigWorld.player().cell.spawnKeyPointAvatar.chooseSpawnKeyPoint(pointId)

    def _invokeRemoteApplyMethod(self):
        BigWorld.player().cell.spawnKeyPointAvatar.placeVehicle()

    def _getDeltaTime(self):
        return max(self.__closeTime - BigWorld.serverTime(), 0)

    def __updateCloseTime(self):
        for viewComponent in self._viewComponents:
            viewComponent.updateCloseTime(self._getDeltaTime(), self.__cdState)

    def __createNotifier(self):
        return PeriodicNotifier(self._getDeltaTime, self.__updateCloseTime, (1,))

    def __clearNotifier(self):
        if self.__notifier:
            self.__notifier.stopNotification()
            self.__notifier.clear()

    def __closeSpawnPoints(self):
        self.__removeListeners()
        self.__clearNotifier()
        self.__isSpawnPointsVisible = False
        for viewComponent in self._viewComponents:
            viewComponent.closeSpawnPoints()

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias == VIEW_ALIAS.INGAME_MENU:
            self.__ingameMenu = pyEntity
            self.__ingameMenu.onDispose += self.__onIngameMenuDisposed

    def __onIngameMenuDisposed(self, _):
        if self.__isSpawnPointsVisible:
            for viewComponent in self._viewComponents:
                viewComponent.setSpawnPoints(self._points)

        if self.__ingameMenu:
            self.__ingameMenu.onDispose -= self.__onIngameMenuDisposed
            self.__ingameMenu = None
        return

    def __removeListeners(self):
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
