# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/eventpoints_ctrl.py
import logging
import SoundGroups
import WWISE
import BigWorld
import event_points_event_type as _eventType
from PlayerEvents import g_playerEvents
from helpers import dependency
from gui.battle_control.view_components import IViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.EVENT_BATTLE_HINT_TYPES import EVENT_BATTLE_HINT_TYPES
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils import getPlayerName
_logger = logging.getLogger(__name__)
_HINT_TYPES = {_eventType.POINTS_LOST: EVENT_BATTLE_HINT_TYPES.POINTS_LOST,
 _eventType.POINTS_SAVED: EVENT_BATTLE_HINT_TYPES.POINTS_SAVED,
 _eventType.PLAYER_DIED: EVENT_BATTLE_HINT_TYPES.POINTS_LOST}
_DRON_START_SOULS_COUNT = 20
_DRON_PLAY_SOUND = 'ev_halloween_music_dron'
_DRON_STOP_SOUND = 'ev_halloween_music_dron_stop'
_RTPC_SOULS_COUNT = 'RTPC_ext_halloween_spirit_amount'
_RTPC_STORAGE = 'RTPC_ext_halloween_storage_activity'
_RTPC_STORAGE_OFF = 0
_RTPC_STORAGE_ON = 100

class EventPointsViewController(IViewComponentsController):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(EventPointsViewController, self).__init__()
        self._totalEventPointsCount = 0
        self._currentEventPointsCount = 0
        self.__totalEventPointsCounterUI = None
        self.__currentEventPointsCounterUI = None
        self.__dronSound = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENTPOINTS_VIEW

    def stopControl(self):
        self._totalEventPointsCount = 0
        self._currentEventPointsCount = 0
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        self.__dronSound = None
        return

    def setViewComponents(self, *components):
        self.__totalEventPointsCounterUI = components[0]
        self.__currentEventPointsCounterUI = components[1]
        if self.__totalEventPointsCounterUI:
            self.setTotalEventPointsCount(self._totalEventPointsCount)
        if self.__currentEventPointsCounterUI:
            self.setCurrentEventPointsCount(self._currentEventPointsCount)
            self.__currentEventPointsCounterUI.setNickname(getPlayerName())

    def startControl(self, *args):
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        self.__dronSound = SoundGroups.g_instance.getSound2D(_DRON_PLAY_SOUND)

    def clearViewComponents(self):
        self.__totalEventPointsCounterUI = None
        self.__totalEventPointsCounterUI = None
        return

    def setTotalEventPointsCount(self, killsCount):
        self._totalEventPointsCount = killsCount
        if self.__totalEventPointsCounterUI:
            self.__totalEventPointsCounterUI.setTotalEventPointsCount(self._totalEventPointsCount)
        WWISE.WW_setRTCPGlobal(_RTPC_STORAGE, _RTPC_STORAGE_ON if killsCount > 0 else _RTPC_STORAGE_OFF)

    def setCurrentEventPointsCount(self, killsCount):
        self._currentEventPointsCount = killsCount
        if self.__currentEventPointsCounterUI:
            self.__currentEventPointsCounterUI.setCurrentEventPointsCount(self._currentEventPointsCount)
        if not self.__dronSound.isPlaying and killsCount >= _DRON_START_SOULS_COUNT:
            self.__dronSound.play()
        elif self.__dronSound.isPlaying and killsCount < _DRON_START_SOULS_COUNT:
            SoundGroups.g_instance.playSound2D(_DRON_STOP_SOUND)
        WWISE.WW_setRTCPGlobal(_RTPC_SOULS_COUNT, killsCount)

    def showCurrentEventPointsCounter(self, show):
        if self.__currentEventPointsCounterUI:
            self.__currentEventPointsCounterUI.showCurrentEventPointsCounter(show)

    def onServerEvent(self, event):
        battleSession = self.guiSessionProvider.shared
        avatar = BigWorld.player()
        if avatar and event.vehicleID == avatar.playerVehicleID:
            hintType = _HINT_TYPES.get(event.type)
            if hintType:
                battleSession.battleHints.showHint(hintType, {'count': event.points})
        battleSession.messages.showEventPointsMessage(event)

    def __onRoundFinished(self, winningTeam, reason):
        battleHints = self.guiSessionProvider.shared.battleHints
        battleHints.showHint(EVENT_BATTLE_HINT_TYPES.TOTAL_POINTS_SAVED, {'count': self._totalEventPointsCount})


def createEventPointsViewController(setup):
    return EventPointsViewController(setup)
