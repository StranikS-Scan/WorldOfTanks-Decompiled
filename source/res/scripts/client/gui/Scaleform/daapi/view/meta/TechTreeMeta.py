# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TechTreeMeta.py
from gui.Scaleform.daapi.view.lobby.techtree.research_view import ResearchView

class TechTreeMeta(ResearchView):

    def requestNationTreeData(self):
        self._printOverrideError('requestNationTreeData')

    def getNationTreeData(self, nationName):
        self._printOverrideError('getNationTreeData')

    def getPremiumPanelLabels(self):
        self._printOverrideError('getPremiumPanelLabels')

    def request4Unlock(self, itemCD):
        self._printOverrideError('request4Unlock')

    def goToNextVehicle(self, vehCD):
        self._printOverrideError('goToNextVehicle')

    def onCloseTechTree(self):
        self._printOverrideError('onCloseTechTree')

    def request4VehCompare(self, vehCD):
        self._printOverrideError('request4VehCompare')

    def onBlueprintModeSwitch(self, enabled):
        self._printOverrideError('onBlueprintModeSwitch')

    def onGoToTankCollector(self, nationName):
        self._printOverrideError('onGoToTankCollector')

    def onGoToPremiumShop(self, nationName, level):
        self._printOverrideError('onGoToPremiumShop')

    def as_setAvailableNationsS(self, nations):
        return self.flashObject.as_setAvailableNations(nations) if self._isDAAPIInited() else None

    def as_setSelectedNationS(self, nationName):
        return self.flashObject.as_setSelectedNation(nationName) if self._isDAAPIInited() else None

    def as_refreshNationTreeDataS(self, nationName):
        return self.flashObject.as_refreshNationTreeData(nationName) if self._isDAAPIInited() else None

    def as_setUnlockPropsS(self, data):
        return self.flashObject.as_setUnlockProps(data) if self._isDAAPIInited() else None

    def as_hideNationsBarS(self, value):
        return self.flashObject.as_hideNationsBar(value) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None

    def as_setBlueprintsSwitchButtonStateS(self, enabled, selected, tooltip, visible=True):
        return self.flashObject.as_setBlueprintsSwitchButtonState(enabled, selected, tooltip, visible) if self._isDAAPIInited() else None

    def as_setBlueprintModeS(self, enabled):
        return self.flashObject.as_setBlueprintMode(enabled) if self._isDAAPIInited() else None

    def as_setBlueprintBalanceS(self, balanceVO):
        return self.flashObject.as_setBlueprintBalance(balanceVO) if self._isDAAPIInited() else None

    def as_closePremiumPanelS(self):
        return self.flashObject.as_closePremiumPanel() if self._isDAAPIInited() else None
