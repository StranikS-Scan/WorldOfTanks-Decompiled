# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchMeta.py
from gui.Scaleform.daapi.view.lobby.techtree.research_view import ResearchView

class ResearchMeta(ResearchView):

    def requestResearchData(self):
        self._printOverrideError('requestResearchData')

    def request4Unlock(self, itemCD, topLevel):
        self._printOverrideError('request4Unlock')

    def request4Rent(self, itemCD):
        self._printOverrideError('request4Rent')

    def goToNextVehicle(self, vehCD):
        self._printOverrideError('goToNextVehicle')

    def exitFromResearch(self):
        self._printOverrideError('exitFromResearch')

    def goToVehicleView(self, itemCD):
        self._printOverrideError('goToVehicleView')

    def compareVehicle(self, itemCD):
        self._printOverrideError('compareVehicle')

    def goToPostProgression(self, itemCD):
        self._printOverrideError('goToPostProgression')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setRootDataS(self, data):
        return self.flashObject.as_setRootData(data) if self._isDAAPIInited() else None

    def as_setResearchItemsS(self, nation, raw):
        return self.flashObject.as_setResearchItems(nation, raw) if self._isDAAPIInited() else None

    def as_setFreeXPS(self, freeXP):
        return self.flashObject.as_setFreeXP(freeXP) if self._isDAAPIInited() else None

    def as_setInstalledItemsS(self, data):
        return self.flashObject.as_setInstalledItems(data) if self._isDAAPIInited() else None

    def as_setWalletStatusS(self, walletStatus):
        return self.flashObject.as_setWalletStatus(walletStatus) if self._isDAAPIInited() else None

    def as_setXpInfoLinkageS(self, linkage):
        return self.flashObject.as_setXpInfoLinkage(linkage) if self._isDAAPIInited() else None

    def as_setPostProgressionDataS(self, data):
        return self.flashObject.as_setPostProgressionData(data) if self._isDAAPIInited() else None

    def as_showPostProgressionUnlockAnimationS(self):
        return self.flashObject.as_showPostProgressionUnlockAnimation() if self._isDAAPIInited() else None
