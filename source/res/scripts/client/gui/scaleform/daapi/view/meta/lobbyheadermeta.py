# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyHeaderMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyHeaderMeta(DAAPIModule):

    def menuItemClick(self, alias):
        self._printOverrideError('menuItemClick')

    def showLobbyMenu(self):
        self._printOverrideError('showLobbyMenu')

    def showExchangeWindow(self, initData):
        self._printOverrideError('showExchangeWindow')

    def showExchangeXPWindow(self, initData):
        self._printOverrideError('showExchangeXPWindow')

    def showPremiumDialog(self, event):
        self._printOverrideError('showPremiumDialog')

    def onPayment(self):
        self._printOverrideError('onPayment')

    def getServers(self):
        self._printOverrideError('getServers')

    def relogin(self, id):
        self._printOverrideError('relogin')

    def as_setScreenS(self, alias):
        if self._isDAAPIInited():
            return self.flashObject.as_setScreen(alias)

    def as_setPeripheryChangingS(self, isChanged):
        if self._isDAAPIInited():
            return self.flashObject.as_setPeripheryChanging(isChanged)

    def as_creditsResponseS(self, credits):
        if self._isDAAPIInited():
            return self.flashObject.as_creditsResponse(credits)

    def as_goldResponseS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_goldResponse(gold)

    def as_setWalletStatusS(self, walletStatus):
        if self._isDAAPIInited():
            return self.flashObject.as_setWalletStatus(walletStatus)

    def as_disableRoamingDDS(self, disable):
        if self._isDAAPIInited():
            return self.flashObject.as_disableRoamingDD(disable)

    def as_setFreeXPS(self, freeXP, useFreeXP):
        if self._isDAAPIInited():
            return self.flashObject.as_setFreeXP(freeXP, useFreeXP)

    def as_nameResponseS(self, fullName, name, clan, isTeamKiller, isClan):
        if self._isDAAPIInited():
            return self.flashObject.as_nameResponse(fullName, name, clan, isTeamKiller, isClan)

    def as_setClanEmblemS(self, tID):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(tID)

    def as_setProfileTypeS(self, premiumLabel):
        if self._isDAAPIInited():
            return self.flashObject.as_setProfileType(premiumLabel)

    def as_setPremiumParamsS(self, timeLabel, premiumLabel, isYear):
        if self._isDAAPIInited():
            return self.flashObject.as_setPremiumParams(timeLabel, premiumLabel, isYear)

    def as_setServerStatsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStats(data)

    def as_setServerInfoS(self, serverUserName, tooltipFullData):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerInfo(serverUserName, tooltipFullData)

    def as_premiumResponseS(self, isPremiumAccount):
        if self._isDAAPIInited():
            return self.flashObject.as_premiumResponse(isPremiumAccount)

    def as_setTankNameS(self, name):
        if self._isDAAPIInited():
            return self.flashObject.as_setTankName(name)

    def as_setTankTypeS(self, type):
        if self._isDAAPIInited():
            return self.flashObject.as_setTankType(type)

    def as_setTankEliteS(self, isElite):
        if self._isDAAPIInited():
            return self.flashObject.as_setTankElite(isElite)

    def as_doDisableNavigationS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_doDisableNavigation()
