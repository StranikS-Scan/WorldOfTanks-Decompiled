# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LobbyHeaderMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def menuItemClick(self, alias):
        """
        :param alias:
        :return :
        """
        self._printOverrideError('menuItemClick')

    def showLobbyMenu(self):
        """
        :return :
        """
        self._printOverrideError('showLobbyMenu')

    def showExchangeWindow(self):
        """
        :return :
        """
        self._printOverrideError('showExchangeWindow')

    def showExchangeXPWindow(self):
        """
        :return :
        """
        self._printOverrideError('showExchangeXPWindow')

    def showPremiumDialog(self):
        """
        :return :
        """
        self._printOverrideError('showPremiumDialog')

    def onPayment(self):
        """
        :return :
        """
        self._printOverrideError('onPayment')

    def showSquad(self):
        """
        :return :
        """
        self._printOverrideError('showSquad')

    def fightClick(self, mapID, actionName):
        """
        :param mapID:
        :param actionName:
        :return :
        """
        self._printOverrideError('fightClick')

    def as_setScreenS(self, alias):
        """
        :param alias:
        :return :
        """
        return self.flashObject.as_setScreen(alias) if self._isDAAPIInited() else None

    def as_creditsResponseS(self, credits, btnDoText, tooltip, tooltipType):
        """
        :param credits:
        :param btnDoText:
        :param tooltip:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_creditsResponse(credits, btnDoText, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_goldResponseS(self, gold, btnDoText, tooltip, tooltipType):
        """
        :param gold:
        :param btnDoText:
        :param tooltip:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_goldResponse(gold, btnDoText, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_doDisableNavigationS(self):
        """
        :return :
        """
        return self.flashObject.as_doDisableNavigation() if self._isDAAPIInited() else None

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        """
        :param btnId:
        :param isEnabled:
        :return :
        """
        return self.flashObject.as_doDisableHeaderButton(btnId, isEnabled) if self._isDAAPIInited() else None

    def as_setGoldFishEnabledS(self, isEnabled, playAnimation, tooltip, tooltipType):
        """
        :param isEnabled:
        :param playAnimation:
        :param tooltip:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_setGoldFishEnabled(isEnabled, playAnimation, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateSquadS(self, isInSquad, tooltip, tooltipType, isEvent, icon):
        """
        :param isInSquad:
        :param tooltip:
        :param tooltipType:
        :param isEvent:
        :param icon:
        :return :
        """
        return self.flashObject.as_updateSquad(isInSquad, tooltip, tooltipType, isEvent, icon) if self._isDAAPIInited() else None

    def as_nameResponseS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_nameResponse(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, tID):
        """
        :param tID:
        :return :
        """
        return self.flashObject.as_setClanEmblem(tID) if self._isDAAPIInited() else None

    def as_setPremiumParamsS(self, btnLabel, doLabel, isHasAction, tooltip, tooltipType):
        """
        :param btnLabel:
        :param doLabel:
        :param isHasAction:
        :param tooltip:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_setPremiumParams(btnLabel, doLabel, isHasAction, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID):
        """
        :param battleTypeName:
        :param battleTypeIcon:
        :param isEnabled:
        :param tooltip:
        :param tooltipType:
        :param battleTypeID:
        :return :
        """
        return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled, tooltip, tooltipType, battleTypeID) if self._isDAAPIInited() else None

    def as_setServerS(self, name, tooltip, tooltipType):
        """
        :param name:
        :param tooltip:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_setServer(name, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_updatePingStatusS(self, pingStatus, isColorBlind):
        """
        :param pingStatus:
        :param isColorBlind:
        :return :
        """
        return self.flashObject.as_updatePingStatus(pingStatus, isColorBlind) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        """
        :param walletStatus:
        :return :
        """
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None

    def as_setFreeXPS(self, freeXP, btnDoText, isHasAction, tooltip, tooltipType):
        """
        :param freeXP:
        :param btnDoText:
        :param isHasAction:
        :param tooltip:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_setFreeXP(freeXP, btnDoText, isHasAction, tooltip, tooltipType) if self._isDAAPIInited() else None

    def as_disableFightButtonS(self, isDisabled):
        """
        :param isDisabled:
        :return :
        """
        return self.flashObject.as_disableFightButton(isDisabled) if self._isDAAPIInited() else None

    def as_setFightButtonS(self, label):
        """
        :param label:
        :return :
        """
        return self.flashObject.as_setFightButton(label) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCoolDownForReady(value) if self._isDAAPIInited() else None

    def as_showBubbleTooltipS(self, message, duration):
        """
        :param message:
        :param duration:
        :return :
        """
        return self.flashObject.as_showBubbleTooltip(message, duration) if self._isDAAPIInited() else None

    def as_setFightBtnTooltipS(self, tooltip):
        """
        :param tooltip:
        :return :
        """
        return self.flashObject.as_setFightBtnTooltip(tooltip) if self._isDAAPIInited() else None

    def as_setHangarMenuDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setHangarMenuData(data) if self._isDAAPIInited() else None
