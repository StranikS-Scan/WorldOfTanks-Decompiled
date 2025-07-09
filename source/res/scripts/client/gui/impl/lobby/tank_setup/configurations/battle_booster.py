# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/configurations/battle_booster.py
from account_helpers.AccountSettings import SHOW_ECONOMIC_DIRECTIVES_HINT, AccountSettings
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.array_providers.battle_booster import OptDeviceBattleBoosterProvider, CrewBattleBoosterProvider, EconomicBattleBoosterProvider
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BattleBoosterTabs(object):
    OPT_DEVICE = 'optDevice'
    CREW = 'crew'
    ECONOMIC = 'economic'
    ALL = (OPT_DEVICE, CREW, ECONOMIC)


class BattleBoostersTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return BattleBoosterTabs.OPT_DEVICE

    @tabUpdateFunc(BattleBoosterTabs.OPT_DEVICE)
    def _updateOptDevice(self, viewModel, isFirst=False):
        pass

    @tabUpdateFunc(BattleBoosterTabs.CREW)
    def _updateCrew(self, viewModel, isFirst=False):
        pass

    @tabUpdateFunc(BattleBoosterTabs.ECONOMIC)
    def _updateEconomic(self, viewModel, isFirst=False):
        pass

    def tabOrderKey(self, tabName):
        return BattleBoosterTabs.ALL.index(tabName)

    def _getAllProviders(self):
        return {BattleBoosterTabs.OPT_DEVICE: OptDeviceBattleBoosterProvider,
         BattleBoosterTabs.CREW: CrewBattleBoosterProvider,
         BattleBoosterTabs.ECONOMIC: EconomicBattleBoosterProvider}


class BattleBoostersIntroductionController(object):
    itemsCache = dependency.descriptor(IItemsCache)
    ECONOMIC_INTRO = 'economic'
    SETTINGS = {ECONOMIC_INTRO: SHOW_ECONOMIC_DIRECTIVES_HINT}
    INTRO_BY_TAB = {BattleBoosterTabs.ECONOMIC: ECONOMIC_INTRO}

    @classmethod
    def getIntroduction(cls, tabName, hasItems):
        if tabName not in cls.INTRO_BY_TAB:
            return None
        else:
            intro = cls.INTRO_BY_TAB[tabName]
            isShown = not AccountSettings.getSettings(cls.SETTINGS[intro])
            return intro if not isShown or not hasItems else None

    @classmethod
    def setIntroductionValue(cls, introName):
        settingName = cls.SETTINGS.get(introName)
        if settingName is not None:
            AccountSettings.setSettings(settingName, False)
        return

    @classmethod
    def getIntroductionType(cls, tabName):
        return cls.INTRO_BY_TAB.get(tabName, '')
