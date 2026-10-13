# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_control/controllers/respawn_ctrl.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from fort_rush.gui.fort_rush_gui_constants import BATTLE_CTRL_ID, VIEW_ALIAS
from fort_rush.helpers.utils import retrievePlayerRespawnComponent
from gui.app_loader import sf_battle
from gui.battle_control.arena_info.interfaces import ISpawnController
from gui.battle_control.view_components import ViewComponentsController
from helpers import dependency, uniprof
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus
from event_platform.gui.shared.events import RespawnFrameworkEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
if TYPE_CHECKING:
    from typing import Dict, Optional, Union
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

    def setSpawnType(self, spawnType):
        pass


class FortRushRespawnViewController(ViewComponentsController, ISpawnController):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FortRushRespawnViewController, self).__init__()
        self.__isSpawnPointsVisible = False
        self.__invulnerableVehicleIDs = set()
        self.__respawnVehicleFilters = None
        self.__eManager = Event.EventManager()
        self.onShowSpawnPoints = Event.Event(self.__eManager)
        self.onCloseSpawnPoints = Event.Event(self.__eManager)
        self.onChooseSpawnPoint = Event.Event(self.__eManager)
        self.onTeamLivesUpdated = Event.Event(self.__eManager)
        self.onTeamRespawnInfoUpdated = Event.Event(self.__eManager)
        self.onTeamLivesSet = Event.Event(self.__eManager)
        self.onVehicleInvulnerabilityChanged = Event.Event(self.__eManager)
        return

    @property
    def isSpawnPointsVisible(self):
        return self.__isSpawnPointsVisible

    def getRespawnVehicleFilters(self):
        return self.__respawnVehicleFilters

    def setRespawnVehicleFilters(self, filters):
        self.__respawnVehicleFilters = dict(filters)

    def getControllerID(self):
        return BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL

    def setVehicleInvulnerable(self, vehicleID, isInvulnerable):
        if isInvulnerable:
            self.__invulnerableVehicleIDs.add(vehicleID)
        else:
            self.__invulnerableVehicleIDs.discard(vehicleID)
        self.onVehicleInvulnerabilityChanged(vehicleID, isInvulnerable)

    def isVehicleInvulnerable(self, vehicleID):
        return vehicleID in self.__invulnerableVehicleIDs

    def startControl(self, *args):
        self.__subscribeListeners()

    def stopControl(self):
        self.__unsubscribeListeners()
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__invulnerableVehicleIDs.clear()
        self.__eManager.clear()
        self.__eManager = None
        return

    def setViewComponents(self, *components):
        self._viewComponents.extend(components)

    def movingToRespawn(self):
        self.closeSpawnPoints()

    def showSpawnPoints(self, points=None):
        uniprof.enterToRegion('avatar.control_mode.fort_rush_spawn_ctrl')
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        else:
            _logger.warning('App reference is still None!')
        _logger.debug('[FORT_RUSH][RESPAWN][VIEW_CTRL] showSpawnPoints')
        respawnComponent = retrievePlayerRespawnComponent()
        if respawnComponent is None:
            return
        else:
            self.__isSpawnPointsVisible = True
            for viewComponent in self._viewComponents:
                viewComponent.setSpawnPoints(respawnComponent.spawnPoints)
                viewComponent.showSpawnPoints()

            self.onShowSpawnPoints(respawnComponent.spawnPoints)
            groupName = respawnComponent.groupName
            if groupName:
                self.onChooseSpawnPoint(groupName)
            return

    def updateSpawnPoints(self, points, pointGuid=None):
        _logger.debug('[FORT_RUSH][RESPAWN][VIEW_CTRL] updateSpawnPoints')
        for viewComponent in self._viewComponents:
            viewComponent.setSpawnPoints(points, pointGuid)

    def closeSpawnPoints(self, event=None):
        uniprof.exitFromRegion('avatar.control_mode.fort_rush_spawn_ctrl')
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        _logger.debug('[FORT_RUSH][RESPAWN][VIEW_CTRL] closeSpawnPoints')
        self.__isSpawnPointsVisible = False
        for viewComponent in self._viewComponents:
            viewComponent.closeSpawnPoints()

        self.onCloseSpawnPoints()

    def chooseSpawnKeyPoint(self, pointId):
        _logger.debug('[FORT_RUSH][RESPAWN][VIEW_CTRL] chooseSpawnKeyPoint: %s', pointId)
        for viewComponent in self._viewComponents:
            viewComponent.onSelectPoint(pointId)

        respawnComponent = retrievePlayerRespawnComponent()
        if respawnComponent is None:
            return
        else:
            respawnComponent.chooseSpawnGroup(pointId)
            self.onChooseSpawnPoint(pointId)
            return

    def addRuntimeView(self, view):
        if view in self._viewComponents:
            _logger.warning('View is already added! %s', view)
        else:
            if self.__isSpawnPointsVisible:
                view.showSpawnPoints()
            self._viewComponents.append(view)

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)
        else:
            _logger.warning('View has not been found! %s', view)

    @sf_battle
    def _app(self):
        return None

    def __subscribeListeners(self):
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_eventBus.addListener(RespawnFrameworkEvent.POSTMORTEM_ENTERED, self.showSpawnPoints, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(RespawnFrameworkEvent.POSTMORTEM_LEFT, self.closeSpawnPoints, scope=EVENT_BUS_SCOPE.BATTLE)

    def __unsubscribeListeners(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_eventBus.removeListener(RespawnFrameworkEvent.POSTMORTEM_ENTERED, self.showSpawnPoints, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(RespawnFrameworkEvent.POSTMORTEM_LEFT, self.closeSpawnPoints, scope=EVENT_BUS_SCOPE.BATTLE)

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
