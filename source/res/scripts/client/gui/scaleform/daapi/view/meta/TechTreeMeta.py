# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TechTreeMeta.py
from gui.Scaleform.daapi.view.lobby.techtree.ResearchView import ResearchView

class TechTreeMeta(ResearchView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ResearchView
    null
    """

    def requestNationTreeData(self):
        """
        :return :
        """
        self._printOverrideError('requestNationTreeData')

    def getNationTreeData(self, nationName):
        """
        :param nationName:
        :return Object:
        """
        self._printOverrideError('getNationTreeData')

    def goToNextVehicle(self, vehCD):
        """
        :param vehCD:
        :return :
        """
        self._printOverrideError('goToNextVehicle')

    def onCloseTechTree(self):
        """
        :return :
        """
        self._printOverrideError('onCloseTechTree')

    def as_setAvailableNationsS(self, nations):
        """
        :param nations:
        :return :
        """
        return self.flashObject.as_setAvailableNations(nations) if self._isDAAPIInited() else None

    def as_setSelectedNationS(self, nationName):
        """
        :param nationName:
        :return :
        """
        return self.flashObject.as_setSelectedNation(nationName) if self._isDAAPIInited() else None

    def as_refreshNationTreeDataS(self, nationName):
        """
        :param nationName:
        :return :
        """
        return self.flashObject.as_refreshNationTreeData(nationName) if self._isDAAPIInited() else None

    def as_setUnlockPropsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setUnlockProps(data) if self._isDAAPIInited() else None

    def as_showMiniClientInfoS(self, description, hyperlink):
        """
        :param description:
        :param hyperlink:
        :return :
        """
        return self.flashObject.as_showMiniClientInfo(description, hyperlink) if self._isDAAPIInited() else None
