# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/sub_systems/hangar_gui_dynamic_economics.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.hangar_presets.providers.base_dynamic_gui_provider import IHangarDynamicGuiProvider

class HangarGuiDynamicEconomics(IHangarGuiController.IHangarGuiDynamicEconomics):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, providersHolder):
        self.__providersHolder = providersHolder

    def fini(self):
        self.__providersHolder = None
        return

    def checkBonusCaps(self, bonusType, bonusCaps):
        guiProvider = self.__providersHolder.getBonusGuiProvider(bonusType)
        return self.__checkBonusCaps(bonusType, bonusCaps, guiProvider)

    def checkCurrentBonusCaps(self, bonusCaps, default=False):
        guiProvider = self.__providersHolder.getCurrentGuiProvider()
        bType = guiProvider.getSuggestedBonusType()
        return self.__checkBonusCaps(bType, bonusCaps, guiProvider) if bType != ARENA_BONUS_TYPE.UNKNOWN else default

    def checkCrystalRewards(self, bonusType):
        guiProvider = self.__providersHolder.getBonusGuiProvider(bonusType)
        return self.__checkCrystalRewards(bonusType, guiProvider)

    def checkCurrentCrystalRewards(self, default=False):
        guiProvider = self.__providersHolder.getCurrentGuiProvider()
        bType = guiProvider.getSuggestedBonusType()
        return self.__checkCrystalRewards(bType, guiProvider) if bType != ARENA_BONUS_TYPE.UNKNOWN else default

    def __checkBonusCaps(self, bonusType, bonusCaps, guiProvider):
        return BONUS_CAPS.checkAny(bonusType, bonusCaps, specificOverrides=guiProvider.getBonusCapsOverrides())

    def __checkCrystalRewards(self, bonusType, guiProvider):
        crystalConfig = self.__lobbyContext.getServerSettings().getCrystalRewardConfig()
        return crystalConfig.isCrystalEarnPossible(bonusType, battleModifiers=guiProvider.getBattleModifiers())
