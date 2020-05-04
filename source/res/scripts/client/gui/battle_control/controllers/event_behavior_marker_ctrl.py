# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_behavior_marker_ctrl.py
import BigWorld
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import isPlayerAvatar

class EventBehaviorMarkersController(IArenaVehiclesController, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        GameEventGetterMixin.__init__(self)

    def startControl(self, battleCtx, arenaVisitor):
        self.behaviorMarker.onUpdated += self.updateBehaviorMarker
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotBehaviorUpdate += self.updateBehaviorMarker

    def stopControl(self):
        self.behaviorMarker.onUpdated -= self.updateBehaviorMarker
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotBehaviorUpdate -= self.updateBehaviorMarker

    def getControllerID(self):
        return BATTLE_CTRL_ID.BEHAVIOR_MARKER

    def spaceLoadCompleted(self):
        self.updateBehaviorMarker()

    def updateBehaviorMarker(self):
        behaviorMarkers = self.behaviorMarker.getParams()
        for vehId in behaviorMarkers:
            self.__update(vehId, behaviorMarkers)

    def updateBehaviorMarkerById(self, vehicleID):
        behaviorMarkers = self.behaviorMarker.getParams()
        if vehicleID in behaviorMarkers:
            self.__update(vehicleID, behaviorMarkers)

    def __update(self, vehicleID, behaviorMarkers):
        if not isPlayerAvatar():
            return
        player = BigWorld.player()
        data = behaviorMarkers[vehicleID]
        if data['show']:
            player.onBotBehaviorReceived(vehicleID, data['markerType'])
        else:
            player.onBotBehaviorReceived(vehicleID)
