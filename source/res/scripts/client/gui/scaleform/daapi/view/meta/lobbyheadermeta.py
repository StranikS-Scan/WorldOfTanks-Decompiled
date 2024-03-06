# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LobbyHeaderMeta(BaseDAAPIComponent):

    def menuItemClick(self, alias):
        self._printOverrideError('menuItemClick')

    def showLobbyMenu(self):
        self._printOverrideError('showLobbyMenu')

    def showDashboard(self):
        self._printOverrideError('showDashboard')

    def showExchangeWindow(self):
        self._printOverrideError('showExchangeWindow')

    def showExchangeXPWindow(self):
        self._printOverrideError('showExchangeXPWindow')

    def showWotPlusView(self):
        self._printOverrideError('showWotPlusView')

    def showPremiumView(self):
        self._printOverrideError('showPremiumView')

    def onPremShopClick(self):
        self._printOverrideError('onPremShopClick')

    def onReservesClick(self):
        self._printOverrideError('onReservesClick')

    def onCrystalClick(self):
        self._printOverrideError('onCrystalClick')

    def onPayment(self):
        self._printOverrideError('onPayment')

    def movePlatoonPopover(self, popoverCenterX):
        self._printOverrideError('movePlatoonPopover')

    def showSquad(self, popoverCenterX):
        self._printOverrideError('showSquad')

    def openFullscreenBattleSelector(self):
        self._printOverrideError('openFullscreenBattleSelector')

    def closeFullscreenBattleSelector(self):
        self._printOverrideError('closeFullscreenBattleSelector')

    def fightClick(self, mapID, actionName):
        self._printOverrideError('fightClick')

    def as_setScreenS(self, alias):
        return self.flashObject.as_setScreen(alias) if self._isDAAPIInited() else None

    def as_updateWalletBtnS(self, btnID, data):
        return self.flashObject.as_updateWalletBtn(btnID, data) if self._isDAAPIInited() else None

    def as_doDisableNavigationS(self):
        return self.flashObject.as_doDisableNavigation() if self._isDAAPIInited() else None

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        return self.flashObject.as_doDisableHeaderButton(btnId, isEnabled) if self._isDAAPIInited() else None

    def as_doSoftDisableHeaderButtonS(self, btnId, isSoftDisable):
        return self.flashObject.as_doSoftDisableHeaderButton(btnId, isSoftDisable) if self._isDAAPIInited() else None

    def as_doDeselectHeaderButtonS(self, alias):
        return self.flashObject.as_doDeselectHeaderButton(alias) if self._isDAAPIInited() else None

    def as_setGoldFishEnabledS(self, isEnabled, playAnimation, tooltip, tooltipType):
        return self.flashObject.as_setGoldFishEnabled(isEnabled, playAnimation, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateSquadS(self, isInSquad, tooltip, tooltipType, isEvent, icon, hasPopover, eventBgLinkage, data):
        return self.flashObject.as_updateSquad(isInSquad, tooltip, tooltipType, isEvent, icon, hasPopover, eventBgLinkage, data) if self._isDAAPIInited() else None

    def as_nameResponseS(self, data):
        return self.flashObject.as_nameResponse(data) if self._isDAAPIInited() else None

    def as_setBadgeS(self, data, selected):
        return self.flashObject.as_setBadge(data, selected) if self._isDAAPIInited() else None

    def as_setWotPlusDataS(self, data):
        return self.flashObject.as_setWotPlusData(data) if self._isDAAPIInited() else None

    def as_setPremiumParamsS(self, data):
        return self.flashObject.as_setPremiumParams(data) if self._isDAAPIInited() else None

    def as_setPremShopDataS(self, iconSrc, premShopText, tooltip, tooltipType):
        return self.flashObject.as_setPremShopData(iconSrc, premShopText, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID, eventAnimEnabled, eventBgLinkage, showLegacySelector, hasNew):
        return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID, eventAnimEnabled, eventBgLinkage, showLegacySelector, hasNew) if self._isDAAPIInited() else None

    def as_setServerS(self, name, tooltip, tooltipType):
        return self.flashObject.as_setServer(name, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updatePingStatusS(self, pingStatus, isColorBlind):
        return self.flashObject.as_updatePingStatus(pingStatus, isColorBlind) if self._isDAAPIInited() else None

    def as_updateAnonymizedStateS(self, isAnonymized):
        return self.flashObject.as_updateAnonymizedState(isAnonymized) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None

    def as_disableFightButtonS(self, isDisabled):
        return self.flashObject.as_disableFightButton(isDisabled) if self._isDAAPIInited() else None

    def as_setFightButtonS(self, label):
        return self.flashObject.as_setFightButton(label) if self._isDAAPIInited() else None

    def as_setFightButtonHighlightS(self, linkage):
        return self.flashObject.as_setFightButtonHighlight(linkage) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyS(self, value):
        return self.flashObject.as_setCoolDownForReady(value) if self._isDAAPIInited() else None

    def as_showBubbleTooltipS(self, message, duration):
        return self.flashObject.as_showBubbleTooltip(message, duration) if self._isDAAPIInited() else None

    def as_setFightBtnTooltipS(self, tooltip, isSpecial):
        return self.flashObject.as_setFightBtnTooltip(tooltip, isSpecial) if self._isDAAPIInited() else None

    def as_updateOnlineCounterS(self, clusterStats, regionStats, tooltip, isAvailable):
        return self.flashObject.as_updateOnlineCounter(clusterStats, regionStats, tooltip, isAvailable) if self._isDAAPIInited() else None

    def as_initOnlineCounterS(self, visible):
        return self.flashObject.as_initOnlineCounter(visible) if self._isDAAPIInited() else None

    def as_setServerNameS(self, value):
        return self.flashObject.as_setServerName(value) if self._isDAAPIInited() else None

    def as_setHangarMenuDataS(self, data):
        return self.flashObject.as_setHangarMenuData(data) if self._isDAAPIInited() else None

    def as_setButtonCounterS(self, btnAlias, value):
        return self.flashObject.as_setButtonCounter(btnAlias, value) if self._isDAAPIInited() else None

    def as_removeButtonCounterS(self, btnAlias):
        return self.flashObject.as_removeButtonCounter(btnAlias) if self._isDAAPIInited() else None

    def as_setHeaderButtonsS(self, data):
        return self.flashObject.as_setHeaderButtons(data) if self._isDAAPIInited() else None

    def as_hideMenuS(self, value):
        return self.flashObject.as_hideMenu(value) if self._isDAAPIInited() else None

    def as_toggleVisibilityMenuS(self, state):
        return self.flashObject.as_toggleVisibilityMenu(state) if self._isDAAPIInited() else None

    def as_setIsPlatoonDropdownShowingS(self, visible):
        return self.flashObject.as_setIsPlatoonDropdownShowing(visible) if self._isDAAPIInited() else None

    def as_setIsFullscreenBattleSelectorShowingS(self, visible):
        return self.flashObject.as_setIsFullscreenBattleSelectorShowing(visible) if self._isDAAPIInited() else None

    def as_setButtonHighlightS(self, btnAlias, isHighlighted):
        return self.flashObject.as_setButtonHighlight(btnAlias, isHighlighted) if self._isDAAPIInited() else None
