# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/br_vo_controller.py
import WWISE
from constants import CURRENT_REALM
import Settings
from gui.game_control.br_lobby_vo import BRLobbyVO
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_BONUS_TYPE

class BRVoiceOverController(object):
    __SWITCH_RU = 'SWITCH_ext_BR_vo_language'
    __SWITCH_RU_ON = 'SWITCH_ext_BR_vo_language_RU'
    __SWITCH_RU_OFF = 'SWITCH_ext_BR_vo_language_nonRU'
    __RU_REALMS = ('DEV', 'QA', 'RU')
    __ENABLE_VO_KEY = 'br_enable_ru_vo'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BRVoiceOverController, self).__init__()
        self.__lobbyVO = None
        self.__wasInBR = False
        self.__isActive = False
        self.__lobbySoundPosition = None
        self.__battleResultsShown = False
        soundPref = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        self.__isEnabled = soundPref.readBool(self.__ENABLE_VO_KEY, True)
        WWISE.WW_setRuVoEnabled(self.__isVO)
        return

    def destroy(self):
        soundPref = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        soundPref.writeBool(self.__ENABLE_VO_KEY, self.__isEnabled)
        self.__destroyLobbyVO()

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isRuRealm(self):
        return CURRENT_REALM in self.__RU_REALMS

    def setEnabled(self, isEnabled):
        self.__isEnabled = isEnabled
        self.__updateLobbySwitch()

    def onConnected(self):
        self.__wasInBR = False
        self.__battleResultsShown = False
        if self.isRuRealm:
            self.__lobbyVO = BRLobbyVO()

    def onDisconnected(self):
        self.__destroyLobbyVO()

    def onAvatarBecomePlayer(self):
        arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        self.__wasInBR = arenaBonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE
        if self.__isActive:
            self.__destroyVOSound()
        self.__updateBattleSwitch()

    def activate(self):
        self.__isActive = True
        self.__tryCreateLobbyVOSound()

    def deactivate(self):
        self.__isActive = False
        if self.__lobbyVO is not None:
            self.__lobbyVO.restore()
        self.__destroyVOSound()
        return

    def setLobbyVOPosition(self, position):
        self.__lobbySoundPosition = position
        self.__tryCreateLobbyVOSound()

    def setBattleResultsShown(self, isShown):
        self.__battleResultsShown = isShown
        self.__tryCreateLobbyVOSound()

    def __tryCreateLobbyVOSound(self):
        if self.__lobbyVO is None:
            return
        else:
            if self.__isActive and self.__lobbySoundPosition is not None and not self.__battleResultsShown:
                self.__lobbyVO.createVOSound(self.__wasInBR, self.__lobbySoundPosition)
                self.__lobbyVO.setSwitch(self.__SWITCH_RU, self.__switchValue)
            return

    def __updateLobbySwitch(self):
        if self.__isActive:
            WWISE.WW_setRuVoEnabled(self.__isVO)
            if self.__lobbyVO is not None:
                self.__lobbyVO.setSwitch(self.__SWITCH_RU, self.__switchValue)
        return

    def __updateBattleSwitch(self):
        if self.__isActive:
            WWISE.WW_setSwitch(self.__SWITCH_RU, self.__switchValue)
            WWISE.WW_setRuVoEnabled(self.__isVO)

    def __destroyVOSound(self):
        if self.__lobbyVO is not None:
            self.__lobbyVO.destroyVOSound()
        return

    def __destroyLobbyVO(self):
        if self.__lobbyVO is not None:
            self.__lobbyVO.destroy()
            self.__lobbyVO = None
        return

    @property
    def __isVO(self):
        return self.isRuRealm and self.isEnabled

    @property
    def __switchValue(self):
        return self.__SWITCH_RU_ON if self.__isVO else self.__SWITCH_RU_OFF
