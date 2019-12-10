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

    def showPremiumDialog(self):
        self._printOverrideError('showPremiumDialog')

    def onPremShopClick(self):
        self._printOverrideError('onPremShopClick')

    def onCrystalClick(self):
        self._printOverrideError('onCrystalClick')

    def onPayment(self):
        self._printOverrideError('onPayment')

    def showSquad(self):
        self._printOverrideError('showSquad')

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

    def as_doDeselectHeaderButtonS(self, alias):
        return self.flashObject.as_doDeselectHeaderButton(alias) if self._isDAAPIInited() else None

    def as_setGoldFishEnabledS(self, isEnabled, playAnimation, tooltip, tooltipType):
        return self.flashObject.as_setGoldFishEnabled(isEnabled, playAnimation, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateSquadS(self, isInSquad, tooltip, tooltipType, isEvent, icon):
        return self.flashObject.as_updateSquad(isInSquad, tooltip, tooltipType, isEvent, icon) if self._isDAAPIInited() else None

    def as_nameResponseS(self, data):
        return self.flashObject.as_nameResponse(data) if self._isDAAPIInited() else None

    def as_setBadgeIconS(self, tID):
        return self.flashObject.as_setBadgeIcon(tID) if self._isDAAPIInited() else None

    def as_setBoosterDataS(self, data):
        return self.flashObject.as_setBoosterData(data) if self._isDAAPIInited() else None

    def as_setPremiumParamsS(self, data):
        return self.flashObject.as_setPremiumParams(data) if self._isDAAPIInited() else None

    def as_setPremShopDataS(self, iconSrc, premShopText, tooltip, tooltipType):
        return self.flashObject.as_setPremShopData(iconSrc, premShopText, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID, eventBgEnabled, eventAnimEnabled):
        return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID, eventBgEnabled, eventAnimEnabled) if self._isDAAPIInited() else None

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

    def as_updateNYVisibilityS(self, isShowBattleBtnGlow, isShowMainMenuGlow, nyWidgetVisible):
        return self.flashObject.as_updateNYVisibility(isShowBattleBtnGlow, isShowMainMenuGlow, nyWidgetVisible) if self._isDAAPIInited() else None

    def as_showOrHideNyWidgetS(self, visible):
        return self.flashObject.as_showOrHideNyWidget(visible) if self._isDAAPIInited() else None
