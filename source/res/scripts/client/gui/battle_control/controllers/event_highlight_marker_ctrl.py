# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_highlight_marker_ctrl.py
from functools import partial
import Event
import BigWorld
import SoundGroups
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers import isPlayerAvatar
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from skeletons.gui.battle_session import IBattleSessionProvider

class EventHighlightMarkersController(IArenaVehiclesController, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        GameEventGetterMixin.__init__(self)
        self.__eManager = Event.EventManager()
        self.onMiniMapUpdated = Event.Event(self.__eManager)
        self.__gameEventStorage = None
        self._callbackIds = {}
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.highlightMarkers.onUpdated += self.__updateHighlightMarker

    def stopControl(self):
        self.highlightMarkers.onUpdated -= self.__updateHighlightMarker
        for callbackId in self._callbackIds.itervalues():
            BigWorld.cancelCallback(callbackId)

        self._callbackIds = {}

    def getControllerID(self):
        return BATTLE_CTRL_ID.HIGHLIGHT_MARKER

    def __updateHighlightMarker(self):
        if not isPlayerAvatar():
            return
        else:
            highlightMarkers = self.highlightMarkers.getParams()
            for vehicleID in highlightMarkers:
                data = highlightMarkers[vehicleID]
                vehicle = BigWorld.entities.get(vehicleID)
                if data['show'] and vehicleID not in self._callbackIds:
                    position = vehicle.position if vehicle else data['position']
                    self.onMiniMapUpdated(vehicleID, position, data['classTag'])
                    soundID = data['soundID']
                    sound = SoundGroups.g_instance.getSound2D(soundID) if soundID else None
                    if sound:
                        sound.play()
                    self._callbackIds[vehicleID] = BigWorld.callback(data['duration'], partial(self._stopShow, vehicleID, sound))

            return

    def _stopShow(self, vehicleID, sound):
        del self._callbackIds[vehicleID]
        self.onMiniMapUpdated(vehicleID, None)
        if sound:
            sound.stop()
        return
