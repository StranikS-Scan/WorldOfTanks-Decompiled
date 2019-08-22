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

    def showSpawnPoints(self):
        pass

    def closeSpawnPoints(self):
        pass

    def updatePoint(self, vehicleId, pointId, prevPointId):
        pass

    def updateCloseTime(self, timeLeft, state):
        pass

    def onSelectPoint(self, pointId):
        pass


class SpawnController(ViewComponentsController, ISpawnController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SpawnController, self).__init__()
        self.__ingameMenu = None
        self.__isSpawnPointsVisible = False
        self.__pointsByVehicle = {}
        self.__closeTime = 0
        self.__cdState = COUNTDOWN_STATE.WAIT
        self.__notifier = self.__createNotifier()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPAWN_CTRL

    def startControl(self, *args):
        pass

    def stopControl(self):
        if self._app:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__notifier = None
        return

    def setViewComponents(self, *components):
        self._viewComponents.extend(components)
        self.__updateCloseTime()

    def showSpawnPoints(self, points):
        if self._app:
            self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        else:
            _logger.warning('App reference is still None!')
        self.__isSpawnPointsVisible = True
        for viewComponent in self._viewComponents:
            viewComponent.setSpawnPoints(points)
            viewComponent.showSpawnPoints()

    def setupCloseTime(self, closeTime):
        self.__closeTime = closeTime
        self.__cdState = COUNTDOWN_STATE.START
        self.__notifier.startNotification()

    def updateTeamSpawnKeyPoints(self, points):
        if not self.__isSpawnPointsVisible:
            return
        else:
            arenaDP = self.__sessionProvider.getArenaDP()
            for point in points:
                pointId = point['guid']
                vehicleId = point['vehID']
                if vehicleId == arenaDP.getPlayerVehicleID():
                    continue
                prevPoint = self.__pointsByVehicle.get(vehicleId, None)
                if prevPoint != pointId:
                    for viewComponent in self._viewComponents:
                        viewComponent.updatePoint(vehicleId, pointId, prevPoint)

                    self.__pointsByVehicle[vehicleId] = pointId

            return

    def closeSpawnPoints(self):
        self.__closeSpawnPoints()

    def chooseSpawnKeyPoint(self, pointId):
        for viewComponent in self._viewComponents:
            viewComponent.onSelectPoint(pointId)

        BigWorld.player().cell.chooseSpawnKeyPoint(pointId)

    def placeVehicle(self):
        BigWorld.player().cell.placeVehicle()
        self.__closeSpawnPoints()

    def addRuntimeView(self, view):
        if view in self._viewComponents:
            LOG_ERROR('View is already added! {}'.format(view))
        else:
            if self.__isSpawnPointsVisible:
                view.showSpawnPoints()
            self._viewComponents.append(view)

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)
        else:
            LOG_WARNING('View has not been found! {}'.format(view))

    @sf_battle
    def _app(self):
        return None

    def __updateCloseTime(self):
        for viewComponent in self._viewComponents:
            viewComponent.updateCloseTime(self._getDeltaTime(), self.__cdState)

    def _getDeltaTime(self):
        return max(self.__closeTime - BigWorld.serverTime(), 0)

    def __createNotifier(self):
        return PeriodicNotifier(self._getDeltaTime, self.__updateCloseTime, (1,))

    def __closeSpawnPoints(self):
        if self._app:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
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
                viewComponent.showSpawnPoints()

        if self.__ingameMenu:
            self.__ingameMenu.onDispose -= self.__onIngameMenuDisposed
            self.__ingameMenu = None
        return
