# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LobbyHeaderMeta(BaseDAAPIComponent):

    def menuItemClick(self, alias):
        self._printOverrideError('menuItemClick')

    def showLobbyMenu(self):
        self._printOverrideError('showLobbyMenu')

    def showExchangeWindow(self):
        self._printOverrideError('showExchangeWindow')

    def showExchangeXPWindow(self):
        self._printOverrideError('showExchangeXPWindow')

    def showPremiumDialog(self):
        self._printOverrideError('showPremiumDialog')

    def onPayment(self):
        self._printOverrideError('onPayment')

    def showSquad(self):
        self._printOverrideError('showSquad')

    def fightClick(self, mapID, actionName):
        self._printOverrideError('fightClick')

    def as_setScreenS(self, alias):
        return self.flashObject.as_setScreen(alias) if self._isDAAPIInited() else None

    def as_creditsResponseS(self, credits, btnDoText, tooltip, tooltipType):
        return self.flashObject.as_creditsResponse(credits, btnDoText, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_goldResponseS(self, gold, btnDoText, tooltip, tooltipType):
        return self.flashObject.as_goldResponse(gold, btnDoText, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_doDisableNavigationS(self):
        return self.flashObject.as_doDisableNavigation() if self._isDAAPIInited() else None

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        return self.flashObject.as_doDisableHeaderButton(btnId, isEnabled) if self._isDAAPIInited() else None

    def as_setGoldFishEnabledS(self, isEnabled, playAnimation, tooltip, tooltipType):
        return self.flashObject.as_setGoldFishEnabled(isEnabled, playAnimation, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateSquadS(self, isInSquad, tooltip, tooltipType):
        return self.flashObject.as_updateSquad(isInSquad, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_nameResponseS(self, fullName, name, clan, isTeamKiller, isClan, hasNew, hasActiveBooster, tooltip, tooltipType):
        return self.flashObject.as_nameResponse(fullName, name, clan, isTeamKiller, isClan, hasNew, hasActiveBooster, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, tID):
        return self.flashObject.as_setClanEmblem(tID) if self._isDAAPIInited() else None

    def as_setPremiumParamsS(self, isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody, isHasAction, tooltip, tooltipType):
        return self.flashObject.as_setPremiumParams(isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody, isHasAction, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID):
        return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID) if self._isDAAPIInited() else None

    def as_setServerS(self, name, tooltip, tooltipType):
        return self.flashObject.as_setServer(name, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None

    def as_setFreeXPS(self, freeXP, btnDoText, isHasAction, tooltip, tooltipType):
        return self.flashObject.as_setFreeXP(freeXP, btnDoText, isHasAction, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_disableFightButtonS(self, isDisabled):
        return self.flashObject.as_disableFightButton(isDisabled) if self._isDAAPIInited() else None

    def as_setFightButtonS(self, label):
        return self.flashObject.as_setFightButton(label) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyS(self, value):
        return self.flashObject.as_setCoolDownForReady(value) if self._isDAAPIInited() else None

    def as_showBubbleTooltipS(self, message, duration):
        return self.flashObject.as_showBubbleTooltip(message, duration) if self._isDAAPIInited() else None

    def as_setFightBtnTooltipDataS(self, data):
        return self.flashObject.as_setFightBtnTooltipData(data) if self._isDAAPIInited() else None
