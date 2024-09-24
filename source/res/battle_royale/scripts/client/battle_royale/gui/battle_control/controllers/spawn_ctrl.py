# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/spawn_ctrl.py
import logging
import weakref
import BigWorld
from battle_royale.gui.battle_control.controllers.notification_manager import INotificationManagerListener
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_battle
from gui.battle_control import avatar_getter
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

    def componentChanged(self):
        pass

    def updateRespawnTime(self, timeLeft):
        pass

    def updateTeammateRespawnTime(self, timeLeft):
        pass

    def updateBlockToRessurecTime(self, blockTime):
        pass

    def updateLives(self, livesLeft, prev):
        pass

    def onSelectPoint(self, pointId):
        pass


class SpawnController(ViewComponentsController, ISpawnController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, notificationManager):
        super(SpawnController, self).__init__()
        self.__ingameMenu = None
        self.__isSpawnPointsVisible = False
        self.__pointsByVehicle = {}
        self.__closeTime = 0
        self.__cdState = COUNTDOWN_STATE.WAIT
        self.__notifier = self.__createNotifier()
        self.notificationManager = weakref.ref(notificationManager)
        self.__livesLeft = 0
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPAWN_CTRL

    def startControl(self, *args):
        pass

    def stopControl(self):
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__notifier = None
        self.notificationManager = None
        return

    def setViewComponents(self, *components):
        for component in components:
            if isinstance(component, INotificationManagerListener):
                component.addNotificationManager(self.notificationManager())

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

    def showRespawnPoints(self):
        if self.__isSpawnPointsVisible:
            return
        self.__isSpawnPointsVisible = True
        for viewComponent in self._viewComponents:
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

    def componentChanged(self):
        for viewComponent in self._viewComponents:
            viewComponent.componentChanged()

    def updateRespawnTimer(self, respawnTime):
        for viewComponent in self._viewComponents:
            viewComponent.updateRespawnTime(respawnTime)

    def updateTeammateRespawnTime(self, teammateRespawnTime):
        for viewComponent in self._viewComponents:
            viewComponent.updateTeammateRespawnTime(teammateRespawnTime)

    def updateBlockToRessurecTimer(self, blockTime):
        for viewComponent in self._viewComponents:
            viewComponent.updateBlockToRessurecTime(blockTime)

    def updateLives(self, lives, prev):
        self.__livesLeft = lives
        for viewComponent in self._viewComponents:
            viewComponent.updateLives(lives, prev)

    def closeSpawnPoints(self):
        self.__closeSpawnPoints()

    def chooseSpawnKeyPoint(self, pointId, isRespawn=False):
        for viewComponent in self._viewComponents:
            viewComponent.onSelectPoint(pointId)

        if not isRespawn:
            avatar_getter.getArena().teamInfo.spawnKeyPointTeamInfo.cell.chooseSpawnKeyPoint(pointId)

    def placeVehicle(self):
        avatar_getter.getArena().teamInfo.spawnKeyPointTeamInfo.cell.placeVehicle()
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

    @property
    def viewComponents(self):
        return self._viewComponents

    @property
    def lives(self):
        return self.__livesLeft

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
        if self.__notifier:
            self.__notifier.stopNotification()
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
