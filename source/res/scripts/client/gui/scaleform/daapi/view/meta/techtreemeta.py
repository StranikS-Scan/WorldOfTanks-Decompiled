# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TechTreeMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.techtree.research_view import ResearchView

class TechTreeMeta(ResearchView):

    def requestNationTreeData(self):
        self._printOverrideError('requestNationTreeData')

    def getNationTreeData(self, nationName):
        self._printOverrideError('getNationTreeData')

    def goToNextVehicle(self, vehCD):
        self._printOverrideError('goToNextVehicle')

    def onCloseTechTree(self):
        self._printOverrideError('onCloseTechTree')

    def request4VehCompare(self, vehCD):
        self._printOverrideError('request4VehCompare')

    def as_setAvailableNationsS(self, nations):
        """
        :param nations: Represented by DataProvider (AS)
        """
        return self.flashObject.as_setAvailableNations(nations) if self._isDAAPIInited() else None

    def as_setSelectedNationS(self, nationName):
        return self.flashObject.as_setSelectedNation(nationName) if self._isDAAPIInited() else None

    def as_refreshNationTreeDataS(self, nationName):
        return self.flashObject.as_refreshNationTreeData(nationName) if self._isDAAPIInited() else None

    def as_setUnlockPropsS(self, data):
        """
        :param data: Represented by Array (AS)
        """
        return self.flashObject.as_setUnlockProps(data) if self._isDAAPIInited() else None

    def as_hideNationsBarS(self, value):
        return self.flashObject.as_hideNationsBar(value) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None
