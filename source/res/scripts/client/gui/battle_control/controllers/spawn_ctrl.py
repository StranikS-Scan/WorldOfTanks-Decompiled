# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spawn_ctrl.py
import logging
from enum import IntEnum
import BigWorld
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_battle
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, COUNTDOWN_STATE, VEHICLE_VIEW_STATE
from gui.battle_control.arena_info.interfaces import ISpawnController
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class SpawnType(IntEnum):
    DEFAULT = 1
    TELEPORT = 2


class ISpawnListener(object):

    def setSpawnPoints(self, points, pointId=None):
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

    def setSpawnType(self, spawnType):
        pass


class SpawnController(ViewComponentsController, ISpawnController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SpawnController, self).__init__()
        self._chosenPointGuid = None
        self.__ingameMenu = None
        self.__isSpawnPointsVisible = False
        self.__pointsByVehicle = {}
        self.__closeTime = 0
        self.__cdState = COUNTDOWN_STATE.WAIT
        self.__notifier = self._createNotifier()
        self.__eManager = Event.EventManager()
        self.onShowSpawnPoints = Event.Event(self.__eManager)
        self.onCloseSpawnPoints = Event.Event(self.__eManager)
        self.onChooseSpawnPoint = Event.Event(self.__eManager)
        return

    @property
    def isSpawnPointsVisible(self):
        return self.__isSpawnPointsVisible

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPAWN_CTRL

    def startControl(self, *args):
        self.__subscribeListeners()

    def stopControl(self):
        self.__unsubscribeListeners()
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__notifier = None
        self.__eManager.clear()
        self.__eManager = None
        return

    def setViewComponents(self, *components):
        self._viewComponents.extend(components)
        self._updateCloseTime()

    def showSpawnPoints(self, points, pointGuid=None):
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        else:
            _logger.warning('App reference is still None!')
        self.__isSpawnPointsVisible = True
        for viewComponent in self._viewComponents:
            viewComponent.setSpawnType(self._spawnType)
            viewComponent.setSpawnPoints(points, pointGuid)
            viewComponent.showSpawnPoints()

        self.onShowSpawnPoints(points, pointGuid)

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
        self._closeSpawnPoints()

    def chooseSpawnKeyPoint(self, pointId):
        for viewComponent in self._viewComponents:
            viewComponent.onSelectPoint(pointId)

        self._chosenPointGuid = pointId
        self._chooseSpawnPoint()
        self.onChooseSpawnPoint(pointId)

    def placeVehicle(self):
        self._placeVehicle()
        self._closeSpawnPoints()

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

    @property
    def _spawnType(self):
        return SpawnType.DEFAULT

    def _chooseSpawnPoint(self):
        BigWorld.player().cell.spawnKeyPointAvatar.chooseSpawnKeyPoint(self._chosenPointGuid)

    def _placeVehicle(self):
        BigWorld.player().cell.spawnKeyPointAvatar.placeVehicle()

    def _updateCloseTime(self):
        for viewComponent in self._viewComponents:
            viewComponent.updateCloseTime(self._getDeltaTime(), self.__cdState)

    def _getDeltaTime(self):
        return max(self.__closeTime - BigWorld.serverTime(), 0)

    def _createNotifier(self):
        return PeriodicNotifier(self._getDeltaTime, self._updateCloseTime, (1,))

    def _closeSpawnPoints(self):
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        if self.__notifier:
            self.__notifier.stopNotification()
        self.__isSpawnPointsVisible = False
        for viewComponent in self._viewComponents:
            viewComponent.closeSpawnPoints()

        self.onCloseSpawnPoints()

    def __subscribeListeners(self):
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        vehStateCtrl = self.__sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def __unsubscribeListeners(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        vehStateCtrl = self.__sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

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

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.closeSpawnPoints()

    def __onVehicleStateUpdated(self, state, *_):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.closeSpawnPoints()


class WtSpawnController(SpawnController):

    def __init__(self):
        super(WtSpawnController, self).__init__()
        self._equipment = None
        self._eManager = Event.EventManager()
        self.onTeamLivesUpdated = Event.Event(self._eManager)
        self.onTeamRespawnInfoUpdated = Event.Event(self._eManager)
        self.onTeamLivesSetted = Event.Event(self._eManager)
        return

    def setEquipment(self, equipment):
        self._equipment = equipment

    def cancelEquipment(self):
        if self._equipment:
            self._equipment.deactivate()

    @property
    def _spawnType(self):
        return SpawnType.TELEPORT if self._equipment else SpawnType.DEFAULT

    def _chooseSpawnPoint(self):
        if self._equipment:
            self._applyEquipment()
            self._closeSpawnPoints()
            return
        BigWorld.player().cell.respawnComponent.chooseSpawnPoint(self._chosenPointGuid)

    def _placeVehicle(self):
        pass

    def _applyEquipment(self):
        if self._equipment and self._chosenPointGuid:
            self._equipment.apply(self._chosenPointGuid)

    def _closeSpawnPoints(self):
        super(WtSpawnController, self)._closeSpawnPoints()
        self._equipment = None
        return
