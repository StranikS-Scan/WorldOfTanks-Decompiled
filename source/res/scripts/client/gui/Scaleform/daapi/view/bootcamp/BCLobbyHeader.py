# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCLobbyHeader.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.Scaleform.daapi.view.meta.BCLobbyHeaderMeta import BCLobbyHeaderMeta
from gui.Scaleform.Waiting import Waiting
from bootcamp.BootCampEvents import g_bootcampEvents
from shared_utils import CONST_CONTAINER
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootcampGarage import g_bootcampGarage
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class BCLobbyHeader(BCLobbyHeaderMeta):

    class TABS(CONST_CONTAINER):
        HANGAR = 'hangar'
        STORE = 'store'
        PROFILE = 'profile'
        TECHTREE = 'bootcampLobbyTechTree'
        BARRACKS = 'barracks'
        PREBATTLE = 'prebattle'
        BROWSER = 'browser'
        RESEARCH = 'bootcampLobbyResearch'
        ACADEMY = 'academy'
        MISSIONS = 'missions'
        STRONGHOLD = 'StrongholdView'

    __tabMap = {'MenuHangar': TABS.HANGAR,
     'MenuShop': STORE_CONSTANTS.STORE,
     'MenuProfile': TABS.PROFILE,
     'MenuTechTree': TABS.TECHTREE,
     'MenuBarracks': TABS.BARRACKS,
     'MenuBrowser': TABS.BROWSER,
     'MenuMissions': TABS.MISSIONS}

    def __init__(self):
        BCLobbyHeaderMeta.__init__(self)
        self.__fightButtonDisabled = False
        self.__headerMap = {'HeaderSettings': self.BUTTONS.SETTINGS,
         'HeaderAccount': self.BUTTONS.ACCOUNT,
         'HeaderPremium': self.BUTTONS.PREM,
         'HeaderSquad': self.BUTTONS.SQUAD,
         'HeaderBattleSelector': self.BUTTONS.BATTLE_SELECTOR,
         'HeaderGold': self.BUTTONS.GOLD,
         'HeaderSilver': self.BUTTONS.CREDITS,
         'HeaderFreeExp': self.BUTTONS.FREE_XP}
        self.__tabs = set()

    def _onPopulateEnd(self):
        self.as_initOnlineCounterS(False)
        self.as_setHeaderKeysMapS(self.__headerMap)
        self.as_setMainMenuKeysMapS(self.__tabMap)
        g_bootcampEvents.onBattleReady += self.__updateFightButtonState
        g_bootcampEvents.onBattleNotReady += self.__updateFightButtonState
        g_bootcampEvents.onComponentAppear += self._onComponentAppear
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainerBC

    def _dispose(self):
        g_bootcampEvents.onBattleReady -= self.__updateFightButtonState
        g_bootcampEvents.onBattleNotReady -= self.__updateFightButtonState
        g_bootcampEvents.onComponentAppear -= self._onComponentAppear
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainerBC
        Waiting.hide('updating')
        LobbyHeader._dispose(self)

    def __updateFightButtonState(self):
        self._updatePrebattleControls()
        g_bootcampGarage.highlightLobbyHint('FightButton', not self.__fightButtonDisabled, False)

    def fightClick(self, mapID, actionName):
        g_bootcampEvents.onGarageLessonFinished(0)

    def _onComponentAppear(self, componentId):
        if componentId in self.__tabMap:
            g_bootcamp.updateLobbyLobbySettingsVisibility('hide' + componentId, False)
            self._updateHangarMenuData()
        if componentId in self.__headerMap:
            g_bootcamp.updateLobbyLobbySettingsVisibility('hide' + componentId, False)
            self.updateHeaderButtons()

    def updateHeaderButtons(self):
        bootcampSettings = g_bootcamp.getLobbySettings()
        keys = []
        for key in self.__headerMap:
            if not bootcampSettings['hide' + key]:
                keys.append(self.__headerMap[key])

        self.as_setHeaderButtonsS(keys)

    def updateVisibleComponents(self):
        self._updateHangarMenuData()
        self._updatePrebattleControls()
        self.updateHeaderButtons()

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        if btnId != self.BUTTONS.SETTINGS or btnId != self.BUTTONS.BATTLE_SELECTOR:
            isEnabled = False
        super(LobbyHeader, self).as_doDisableHeaderButtonS(btnId, isEnabled)

    def as_setHangarMenuDataS(self, data):
        tabProvider = data
        tabsToRemove = list()
        self.__tabs.clear()
        bootcampSettings = g_bootcamp.getLobbySettings()
        bootcampItems = {self.TABS.HANGAR: bootcampSettings['hideMenuHangar'],
         STORE_CONSTANTS.STORE: bootcampSettings['hideMenuShop'],
         self.TABS.PROFILE: bootcampSettings['hideMenuProfile'],
         self.TABS.TECHTREE: bootcampSettings['hideMenuTechTree'],
         self.TABS.BARRACKS: bootcampSettings['hideMenuBarracks'],
         self.TABS.BROWSER: bootcampSettings['hideMenuBrowser'],
         self.TABS.MISSIONS: bootcampSettings['hideMenuMissions'],
         self.TABS.STRONGHOLD: bootcampSettings['hideMenuForts'],
         self.TABS.ACADEMY: bootcampSettings['hideMenuAcademy']}
        for item in tabProvider:
            isHideItem = bootcampItems.get(item['value'], False)
            if isHideItem:
                tabsToRemove.append(item)
            item['enabled'] = True
            self.__tabs.add(item['value'])

        for itemToRemove in tabsToRemove:
            tabProvider.remove(itemToRemove)

        BCLobbyHeaderMeta.as_setHangarMenuDataS(self, data)

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID, eventBgEnabled, eventAnim):
        if g_bootcamp.getLessonNum() == g_bootcamp.getContextIntParameter('randomBattleLesson') and battleTypeID != PREBATTLE_ACTION_NAME.RANDOM and battleTypeID != PREBATTLE_ACTION_NAME.BOOTCAMP:
            battleTypeName = BOOTCAMP.GAME_MODE
            battleTypeIcon = RES_ICONS.MAPS_ICONS_BOOTCAMP_EMPTYBATTLESELECTORICON
        LobbyHeader.as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID, False, False)

    def onEnableNavigation(self):
        self.as_doEnableNavigationS()

    def onDisableNavigation(self):
        self.as_doDisableNavigationS()

    def hasCounter(self, alias):
        return alias in self.__tabs

    def _getWalletBtnData(self, btnType, value, formatter, isHasAction=False, isDiscountEnabled=False, isNew=False):
        walletBtnData = super(BCLobbyHeader, self)._getWalletBtnData(btnType, value, formatter, False, False, isNew)
        walletBtnData['btnDoText'] = None
        return walletBtnData

    def _checkFightButtonDisabled(self, canDo, isFightButtonForcedDisabled):
        result = super(BCLobbyHeader, self)._checkFightButtonDisabled(canDo, isFightButtonForcedDisabled)
        self.__fightButtonDisabled = result
        return result

    def _getPremiumLabelText(self, isPremiumAccount, canUpdatePremium):
        pass

    def _getPremiumTooltipText(self, isPremiumAccount, canUpdatePremium):
        pass

    def __onViewAddedToContainerBC(self, _, pyEntity):
        pass
