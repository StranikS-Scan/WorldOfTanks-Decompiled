# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TechTreeMeta.py
from gui.Scaleform.daapi.view.lobby.techtree.ResearchView import ResearchView

class TechTreeMeta(ResearchView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ResearchView
    """

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
        return self.flashObject.as_setAvailableNations(nations) if self._isDAAPIInited() else None

    def as_setSelectedNationS(self, nationName):
        return self.flashObject.as_setSelectedNation(nationName) if self._isDAAPIInited() else None

    def as_refreshNationTreeDataS(self, nationName):
        return self.flashObject.as_refreshNationTreeData(nationName) if self._isDAAPIInited() else None

    def as_setUnlockPropsS(self, data):
        return self.flashObject.as_setUnlockProps(data) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None
