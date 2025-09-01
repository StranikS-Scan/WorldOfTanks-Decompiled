# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/teleport_spawn_ctrl.py
import logging
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_battle
from gui.battle_control import avatar_getter
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from gui.battle_control.arena_info.interfaces import ISpawnController
from helpers import dependency, uniprof
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.skeletons.white_tiger_spawn_listener import ISpawnListener, SpawnType
from white_tiger.cgf_components import wt_sound_helpers
_logger = logging.getLogger(__name__)

class RespawnSoundState(object):
    _STATE_NAME = 'STATE_white_tiger_gameplay_waiting'
    _STATE_SHOWN_VALUE = 'STATE_white_tiger_gameplay_waiting_on'
    _STATE_HIDDEN_VALUE = 'STATE_white_tiger_gameplay_waiting_off'

    def __init__(self):
        self.__activated = False

    def switchOn(self):
        if self.__activated:
            return
        wt_sound_helpers.setState(self._STATE_NAME, self._STATE_SHOWN_VALUE)
        self.__activated = True

    def switchOff(self):
        if not self.__activated:
            return
        wt_sound_helpers.setState(self._STATE_NAME, self._STATE_HIDDEN_VALUE)
        self.__activated = False


class TeleportSpawnController(ViewComponentsController, ISpawnController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TeleportSpawnController, self).__init__()
        self.__ingameMenu = None
        self.__isSpawnPointsVisible = False
        self.__respawnSoundState = RespawnSoundState()
        self.__eManager = Event.EventManager()
        self.onShowSpawnPoints = Event.Event(self.__eManager)
        self.onCloseSpawnPoints = Event.Event(self.__eManager)
        self.onChooseSpawnPoint = Event.Event(self.__eManager)
        self._equipment = None
        self.onTeamLivesUpdated = Event.Event(self.__eManager)
        self.onTeamRespawnInfoUpdated = Event.Event(self.__eManager)
        self.onTeamLivesSetted = Event.Event(self.__eManager)
        return

    def setEquipment(self, equipment):
        self._equipment = equipment

    def cancelEquipment(self):
        if self._equipment:
            self._equipment.deactivate()

    @property
    def isSpawnPointsVisible(self):
        return self.__isSpawnPointsVisible

    def getControllerID(self):
        return BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL

    def startControl(self, *args):
        self.__subscribeListeners()

    def stopControl(self):
        self.__respawnSoundState.switchOff()
        self.__unsubscribeListeners()
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__eManager.clear()
        self.__eManager = None
        return

    def setViewComponents(self, *components):
        self._viewComponents.extend(components)

    def movingToRespawn(self):
        self.closeSpawnPoints()

    def showSpawnPoints(self, points, pointGuid=None):
        uniprof.enterToRegion('avatar.control_mode.teleport_spawn_ctrl')
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        else:
            _logger.warning('App reference is still None!')
        self.__respawnSoundState.switchOn()
        self.__isSpawnPointsVisible = True
        for viewComponent in self._viewComponents:
            viewComponent.setSpawnType(SpawnType.TELEPORT if self._equipment else SpawnType.DEFAULT)
            viewComponent.setSpawnPoints(points, pointGuid)
            viewComponent.showSpawnPoints()

        self.onShowSpawnPoints(points, pointGuid)

    def updateSpawnPoints(self, points, pointGuid=None):
        for viewComponent in self._viewComponents:
            viewComponent.setSpawnPoints(points, pointGuid)

        self.onShowSpawnPoints(points, pointGuid)

    def closeSpawnPoints(self):
        uniprof.exitFromRegion('avatar.control_mode.teleport_spawn_ctrl')
        if self._app and self._app.containerManager:
            self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__isSpawnPointsVisible = False
        for viewComponent in self._viewComponents:
            viewComponent.closeSpawnPoints()

        self.__respawnSoundState.switchOff()
        self.onCloseSpawnPoints()

    def chooseSpawnKeyPoint(self, pointId):
        for viewComponent in self._viewComponents:
            viewComponent.onSelectPoint(pointId)

        if self._equipment:
            self._equipment.apply(pointId)
            self.closeSpawnPoints()
            return
        else:
            avatar_getter.getPlayerVehicle().WTMapPointSelectorComponent.choosePoint(pointId)
            self._equipment = None
            self.onChooseSpawnPoint(pointId)
            return

    def addRuntimeView(self, view):
        if view in self._viewComponents:
            LOG_ERROR('View is already added! %s' % view)
        else:
            if self.__isSpawnPointsVisible:
                view.showSpawnPoints()
            self._viewComponents.append(view)

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)
        else:
            LOG_WARNING('View has not been found! %s' % view)

    @sf_battle
    def _app(self):
        return None

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
