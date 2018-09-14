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
        if self._isDAAPIInited():
            return self.flashObject.as_setScreen(alias)

    def as_creditsResponseS(self, credits, btnDoText, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_creditsResponse(credits, btnDoText, tooltip, tooltipType)

    def as_goldResponseS(self, gold, btnDoText, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_goldResponse(gold, btnDoText, tooltip, tooltipType)

    def as_doDisableNavigationS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_doDisableNavigation()

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_doDisableHeaderButton(btnId, isEnabled)

    def as_setGoldFishEnabledS(self, isEnabled, playAnimation, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_setGoldFishEnabled(isEnabled, playAnimation, tooltip, tooltipType)

    def as_updateSquadS(self, isInSquad, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_updateSquad(isInSquad, tooltip, tooltipType)

    def as_nameResponseS(self, fullName, name, clan, isTeamKiller, isClan, hasNew, hasActiveBooster, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_nameResponse(fullName, name, clan, isTeamKiller, isClan, hasNew, hasActiveBooster, tooltip, tooltipType)

    def as_setClanEmblemS(self, tID):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(tID)

    def as_setPremiumParamsS(self, isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody, isHasAction, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_setPremiumParams(isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody, isHasAction, tooltip, tooltipType)

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID):
        if self._isDAAPIInited():
            return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID)

    def as_setServerS(self, name, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_setServer(name, tooltip, tooltipType)

    def as_setWalletStatusS(self, walletStatus):
        if self._isDAAPIInited():
            return self.flashObject.as_setWalletStatus(walletStatus)

    def as_setFreeXPS(self, freeXP, btnDoText, isHasAction, tooltip, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_setFreeXP(freeXP, btnDoText, isHasAction, tooltip, tooltipType)

    def as_disableFightButtonS(self, isDisabled):
        if self._isDAAPIInited():
            return self.flashObject.as_disableFightButton(isDisabled)

    def as_setFightButtonS(self, label):
        if self._isDAAPIInited():
            return self.flashObject.as_setFightButton(label)

    def as_setCoolDownForReadyS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCoolDownForReady(value)

    def as_showBubbleTooltipS(self, message, duration):
        if self._isDAAPIInited():
            return self.flashObject.as_showBubbleTooltip(message, duration)

    def as_setFightBtnTooltipDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setFightBtnTooltipData(data)
