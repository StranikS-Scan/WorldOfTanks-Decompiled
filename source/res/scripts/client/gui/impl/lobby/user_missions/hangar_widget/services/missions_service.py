# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/missions_service.py
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from constants import QUEUE_TYPE
from gui.impl.lobby.user_missions.hangar_widget.services import IMissionsService
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import g_eventBus, events

class MissionsService(IMissionsService):

    def __init__(self):
        super(MissionsService, self).__init__()
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer

    def onPrbEntitySwitched(self):
        self._onMissionsChangedEvent()

    def isVisible(self):
        isVisible = umgConfigSchema.getModel().enableAllDaily
        isVisible &= self.__isValidBattleType()
        return isVisible

    def startListening(self):
        self.startGlobalListening()
        g_playerEvents.onConfigModelUpdated += self.__onConfigModelUpdated

    def stopListening(self):
        self.stopGlobalListening()
        g_playerEvents.onConfigModelUpdated -= self.__onConfigModelUpdated

    def finalize(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.stopListening()

    def __onLobbyInited(self, *_):
        self.startListening()

    def __onAccountBecomeNonPlayer(self):
        self.stopListening()

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self._onMissionsChangedEvent()

    def __isValidBattleType(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is None:
            return False
        else:
            prbEntity = prbDispatcher.getEntity()
            return False if prbEntity is None else prbEntity.getQueueType() in (QUEUE_TYPE.RANDOMS,
             QUEUE_TYPE.MAPBOX,
             QUEUE_TYPE.WINBACK,
             QUEUE_TYPE.COMP7,
             QUEUE_TYPE.COMP7_LIGHT)

    def _onMissionsChangedEvent(self, *_):
        self.onMissionsChanged()
