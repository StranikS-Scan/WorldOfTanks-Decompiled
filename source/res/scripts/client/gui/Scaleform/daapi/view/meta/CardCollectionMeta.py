# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CardCollectionMeta.py
from gui.Scaleform.framework.entities.View import View

class CardCollectionMeta(View):

    def rewardsScreenButtonClicked(self):
        self._printOverrideError('rewardsScreenButtonClicked')

    def resultsScreenButtonClicked(self):
        self._printOverrideError('resultsScreenButtonClicked')

    def onClose(self, screenId):
        self._printOverrideError('onClose')

    def addNewCardsButtonClicked(self):
        self._printOverrideError('addNewCardsButtonClicked')

    def buffonCardPurchaseButtonClicked(self):
        self._printOverrideError('buffonCardPurchaseButtonClicked')

    def requestForShowingResultScreen(self):
        self._printOverrideError('requestForShowingResultScreen')

    def displayBuffonRecruitmentScreen(self):
        self._printOverrideError('displayBuffonRecruitmentScreen')

    def playSoundFx(self, fxId):
        self._printOverrideError('playSoundFx')

    def as_setStaticDataS(self, data):
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_submitTFMAssignedCardsListS(self, data):
        return self.flashObject.as_submitTFMAssignedCardsList(data) if self._isDAAPIInited() else None

    def as_buffonWasRecruitedS(self):
        return self.flashObject.as_buffonWasRecruited() if self._isDAAPIInited() else None

    def as_initRewardsScreenS(self, data):
        return self.flashObject.as_initRewardsScreen(data) if self._isDAAPIInited() else None

    def as_initResultsScreenS(self, data):
        return self.flashObject.as_initResultsScreen(data) if self._isDAAPIInited() else None

    def as_displayRewardsS(self, value):
        return self.flashObject.as_displayRewards(value) if self._isDAAPIInited() else None

    def as_displayResultsS(self, value, isBuffonAvailable):
        return self.flashObject.as_displayResults(value, isBuffonAvailable) if self._isDAAPIInited() else None

    def as_showCardSlotPurchaseButtonS(self, value):
        return self.flashObject.as_showCardSlotPurchaseButton(value) if self._isDAAPIInited() else None

    def as_updatePlayerCardPointsS(self, playerScore, isMilestoneReached):
        return self.flashObject.as_updatePlayerCardPoints(playerScore, isMilestoneReached) if self._isDAAPIInited() else None

    def as_showCardsPacketScreenS(self):
        return self.flashObject.as_showCardsPacketScreen() if self._isDAAPIInited() else None
