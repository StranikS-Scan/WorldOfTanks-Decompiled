# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spectator_ctrl.py
import Event
import BigWorld
import BattleReplay
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent, DeathCamEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class SPECTATOR_MODE(object):
    NONE = EPIC_CONSTS.TARGET_NONE
    FREECAM = EPIC_CONSTS.SPECTATOR_MODE_FREECAM
    FOLLOW = EPIC_CONSTS.SPECTATOR_MODE_FOLLOW


class ISpectatorViewListener(object):

    def updateSpeedLevel(self, newSpeedLevel):
        pass


class SpectatorViewController(ViewComponentsController):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(SpectatorViewController, self).__init__()
        self.__plugins = {}
        self.__eManager = Event.EventManager()
        self.__mode = SPECTATOR_MODE.NONE
        self.__vehicleID = None
        self.__currentSpeedGear = 3
        self.onSpectatorViewModeChanged = Event.Event(self.__eManager)
        self.onFreeCameraMoved = Event.Event(self.__eManager)
        self.onFreeCameraVerticalMoved = Event.Event(self.__eManager)
        return

    spectatorViewMode = property(lambda self: self.__getViewMode())

    def markerWasHovered(self, isHovered, targetID):
        if not isHovered or targetID is None:
            self.toggleFollowHint(False)
            return
        else:
            player = BigWorld.player()
            vehicleData = self._sessionProvider.getArenaDP().getVehicleInfo(targetID)
            if vehicleData is not None:
                isVehicleAlive = vehicleData.isAlive()
                vehicleTeam = vehicleData.team
                vehicleDescription = vehicleData.vehicleType
                isUnobservable = vehicleDescription and 'unobservable' in vehicleDescription.tags
                if isVehicleAlive and vehicleTeam == player.team and not isUnobservable and self.__getViewMode() != SPECTATOR_MODE.NONE:
                    self.toggleFollowHint(True)
            return

    def toggleFollowHint(self, toggle):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        for viewCmp in self._viewComponents:
            viewCmp.toggleFollowHint(toggle)

    def getCurrentSpeedGear(self):
        return self.__currentSpeedGear

    def spectatorViewModeChanged(self, mode):
        if mode == self.__mode:
            return
        self.__mode = mode
        self.onSpectatorViewModeChanged(mode)
        g_eventBus.handleEvent(GameEvent(DeathCamEvent.DEATH_CAM_SPECTATOR_MODE, ctx={'mode': mode}), scope=EVENT_BUS_SCOPE.BATTLE)

    def freeCamSpeedLevelChanged(self, newSpeedLevel):
        if self.__currentSpeedGear != newSpeedLevel:
            self.__currentSpeedGear = newSpeedLevel
            for viewCmp in self._viewComponents:
                viewCmp.updateSpeedLevel(newSpeedLevel)

    def freeCamMoved(self):
        self.onFreeCameraMoved()

    def freeCamVerticalMoved(self):
        self.onFreeCameraVerticalMoved()

    def getControllerID(self):
        return BATTLE_CTRL_ID.SPECTATOR

    def startControl(self):
        self.onSpectatorViewModeChanged(self.__mode)
        self.freeCamSpeedLevelChanged(self.__currentSpeedGear)

    def stopControl(self):
        self.__eManager.clear()
        self.__eManager = None
        return

    def __getViewMode(self):
        return self.__mode
