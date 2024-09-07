# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/game_control/winback_hints_controller.py
import BigWorld
from account_helpers.AccountSettings import Winback
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from constants import ARENA_BONUS_TYPE
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.decorators import adisp_process
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from tutorial.control.context import GLOBAL_FLAG
from winback.gui.shared.gui_items.processors.winback import WinbackDrawSelectorHintTokenProcessor
from winback.gui.winback_helpers import getWinbackSetting, setWinbackSetting

class WinbackHintsController(object):
    __slots__ = ('__isActive', '__winbackController')
    __settingsCore = dependency.descriptor(ISettingsCore)
    _BATTLE_COUNT_TO_SHOW_SELECTOR_HINT = 15

    def __init__(self):
        self.__isActive = False

    def fini(self):
        self.updateState(False)

    def markSelectorHintAsSeen(self):
        self.__requestResetSelectorHint()

    def updateState(self, isActive):
        if self.__isActive == isActive:
            return
        self.__isActive = isActive
        if isActive:
            g_playerEvents.onAvatarBecomePlayer += self.__onEnterInBattle
            g_playerEvents.onAccountBecomePlayer += self.__updateBattleSelectorHintParameters
        else:
            g_playerEvents.onAvatarBecomePlayer -= self.__onEnterInBattle
            g_playerEvents.onAccountBecomePlayer -= self.__updateBattleSelectorHintParameters

    def __updateBattleSelectorHintParameters(self):
        if self._BATTLE_COUNT_TO_SHOW_SELECTOR_HINT > self.__getWinbackBattlesCount():
            return
        else:
            tutorialStorage = getTutorialGlobalStorage()
            if tutorialStorage is None:
                return
            tutorialStorage.setValue(GLOBAL_FLAG.IS_CHANGE_AI_MODE, True)
            self.__requestResetSelectorHint()
            return

    @classmethod
    def __onEnterInBattle(cls):
        if BigWorld.player().arenaBonusType == ARENA_BONUS_TYPE.VERSUS_AI:
            cls.__incWinbackBattlesCounter()

    @classmethod
    def __incWinbackBattlesCounter(cls):
        battlesCount = cls.__getWinbackBattlesCount()
        setWinbackSetting(Winback.WINBACK_BATTLES_COUNT, battlesCount + 1)

    @classmethod
    @adisp_process('updating')
    def __requestResetSelectorHint(cls):
        result = yield WinbackDrawSelectorHintTokenProcessor().request()
        if result.success:
            cls.__resetSelectorHint()

    @classmethod
    def __resetSelectorHint(cls):
        setWinbackSetting(Winback.WINBACK_BATTLES_COUNT, 0)
        serverSettings = cls.__settingsCore.serverSettings
        if bool(serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.BATTLE_SELECTOR_BAR_AI_HINT)):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.BATTLE_SELECTOR_BAR_AI_HINT: 0})

    @staticmethod
    def __getWinbackBattlesCount():
        return getWinbackSetting(Winback.WINBACK_BATTLES_COUNT)
