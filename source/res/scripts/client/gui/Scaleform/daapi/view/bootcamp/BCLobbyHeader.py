# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCLobbyHeader.py
from bootcamp.BootcampConstants import getBootcampInternalHideElementName
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import LobbyHeader
from gui.Scaleform.Waiting import Waiting
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampGarage import g_bootcampGarage
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
_ALLOWED_ENABLED_BUTTONS = [LobbyHeader.BUTTONS.SETTINGS, LobbyHeader.BUTTONS.BATTLE_SELECTOR]

class BCLobbyHeader(LobbyHeader):
    bootcampCtrl = dependency.descriptor(IBootcampController)
    __tabMap = {'MenuHangar': LobbyHeader.TABS.HANGAR,
     'MenuShop': STORE_CONSTANTS.STORE,
     'MenuProfile': LobbyHeader.TABS.PROFILE,
     'MenuTechTree': LobbyHeader.TABS.TECHTREE,
     'MenuBarracks': LobbyHeader.TABS.BARRACKS,
     'MenuBrowser': LobbyHeader.TABS.BROWSER,
     'MenuMissions': LobbyHeader.TABS.MISSIONS}

    def __init__(self):
        LobbyHeader.__init__(self)
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
        self.__observer = None
        return

    def showNewElements(self, newElements):
        if self.__observer is not None:
            self.__observer.as_showAnimatedS(newElements)
        return

    def fightClick(self, _, __):
        g_bootcampEvents.onGarageLessonFinished(0)

    def updateHeaderButtons(self):
        bootcampSettings = self.bootcampCtrl.getLobbySettings()
        keys = []
        for key in self.__headerMap:
            internalName = getBootcampInternalHideElementName(key)
            if not bootcampSettings[internalName]:
                keys.append(self.__headerMap[key])

        if g_bootcampGarage.isInPreview():
            if self.BUTTONS.BATTLE_SELECTOR in keys:
                keys.remove(self.BUTTONS.BATTLE_SELECTOR)
        if self.__observer is not None:
            self.__observer.as_setHeaderButtonsS(keys)
        return

    def updateVisibleComponents(self, visibleSettings):
        if self.__observer is not None:
            self.__observer.as_setBootcampDataS(visibleSettings)
        self._updateHangarMenuData()
        self._updatePrebattleControls()
        self.updateHeaderButtons()
        return

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        if btnId not in _ALLOWED_ENABLED_BUTTONS:
            isEnabled = False
        super(BCLobbyHeader, self).as_doDisableHeaderButtonS(btnId, isEnabled)

    def hasCounter(self, alias):
        return alias in self.__tabs

    def _getHangarMenuItemDataProvider(self, fortEmblem):
        tabDataProvider = super(BCLobbyHeader, self)._getHangarMenuItemDataProvider(fortEmblem)
        self.__tabs.clear()
        bootcampSettings = self.bootcampCtrl.getLobbySettings()
        bootcampItems = {self.TABS.HANGAR: bootcampSettings['hideMenuHangar'],
         STORE_CONSTANTS.STORE: bootcampSettings['hideMenuShop'],
         self.TABS.PROFILE: bootcampSettings['hideMenuProfile'],
         self.TABS.TECHTREE: bootcampSettings['hideMenuTechTree'],
         self.TABS.BARRACKS: bootcampSettings['hideMenuBarracks'],
         self.TABS.BROWSER: bootcampSettings['hideMenuBrowser'],
         self.TABS.MISSIONS: bootcampSettings['hideMenuMissions'],
         self.TABS.STRONGHOLD: bootcampSettings['hideMenuForts'],
         self.TABS.ACADEMY: bootcampSettings['hideMenuAcademy'],
         self.TABS.PERSONAL_MISSIONS: bootcampSettings['hideMenuMissions']}
        newDataProvider = []
        for item in tabDataProvider:
            if item['value'] in bootcampItems and not bootcampItems[item['value']]:
                item['enabled'] = True
                newDataProvider.append(item)
                self.__tabs.add(item['value'])

        LobbyHeader.as_setHangarMenuDataS(self, newDataProvider)
        return newDataProvider

    def _onComponentAppear(self, componentId):
        if componentId in self.__tabMap:
            hideElement = getBootcampInternalHideElementName(componentId)
            self.bootcampCtrl.updateLobbySettingsVisibility(hideElement, False)
            self._updateHangarMenuData()
        if componentId in self.__headerMap:
            hideElement = getBootcampInternalHideElementName(componentId)
            self.bootcampCtrl.updateLobbySettingsVisibility(hideElement, False)
            self.updateHeaderButtons()

    def _updatePrebattleControls(self):
        super(BCLobbyHeader, self)._updatePrebattleControls()
        if g_bootcampGarage.isInPreview():
            self.as_doDisableHeaderButtonS(self.BUTTONS.BATTLE_SELECTOR, True)
            g_bootcampGarage.highlightLobbyHint('BattleType', False, True)

    def _checkFightButtonDisabled(self, canDo, isFightButtonForcedDisabled):
        result = super(BCLobbyHeader, self)._checkFightButtonDisabled(canDo, isFightButtonForcedDisabled)
        self.__fightButtonDisabled = result
        return result

    def _getWalletBtnDoText(self, _):
        return None

    def _getPremiumLabelText(self, _, __):
        pass

    def _getPremiumTooltipText(self, _, __):
        pass

    def _onPopulateEnd(self):
        self.__observer = self.app.bootcampManager.getObserver('BCLobbyHeaderObserver')
        if self.__observer is not None:
            self.__observer.as_setHeaderKeysMapS(self.__headerMap)
            self.__observer.as_setMainMenuKeysMapS(self.__tabMap)
        self.as_initOnlineCounterS(False)
        g_bootcampEvents.onBattleReady += self.__updateFightButtonState
        g_bootcampEvents.onBattleNotReady += self.__updateFightButtonState
        g_bootcampEvents.onComponentAppear += self._onComponentAppear
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainerBC
        return

    def _dispose(self):
        g_bootcampEvents.onBattleReady -= self.__updateFightButtonState
        g_bootcampEvents.onBattleNotReady -= self.__updateFightButtonState
        g_bootcampEvents.onComponentAppear -= self._onComponentAppear
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainerBC
        self.__observer = None
        Waiting.hide('updating')
        super(BCLobbyHeader, self)._dispose()
        return

    def _getWalletBtnData(self, btnType, value, formatter, isHasAction=False, isDiscountEnabled=False, isNew=False):
        if btnType not in _ALLOWED_ENABLED_BUTTONS:
            isHasAction = False
        return super(BCLobbyHeader, self)._getWalletBtnData(btnType, value, formatter, isHasAction, isDiscountEnabled, isNew)

    def __updateFightButtonState(self):
        self._updatePrebattleControls()
        g_bootcampGarage.highlightLobbyHint('FightButton', not self.__fightButtonDisabled, False)

    def __onViewAddedToContainerBC(self, _, pyEntity):
        pass
