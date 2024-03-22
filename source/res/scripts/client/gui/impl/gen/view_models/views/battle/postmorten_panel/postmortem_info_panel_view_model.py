# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/postmorten_panel/postmortem_info_panel_view_model.py
from frameworks.wulf import ViewModel

class PostmortemInfoPanelViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PostmortemInfoPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFrontline(self):
        return self._getBool(0)

    def setIsFrontline(self, value):
        self._setBool(0, value)

    def getIsFreecamAvailable(self):
        return self._getBool(1)

    def setIsFreecamAvailable(self, value):
        self._setBool(1, value)

    def getIsBlinking(self):
        return self._getBool(2)

    def setIsBlinking(self, value):
        self._setBool(2, value)

    def getHasLivesAvailable(self):
        return self._getBool(3)

    def setHasLivesAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PostmortemInfoPanelViewModel, self)._initialize()
        self._addBoolProperty('isFrontline', False)
        self._addBoolProperty('isFreecamAvailable', False)
        self._addBoolProperty('isBlinking', False)
        self._addBoolProperty('hasLivesAvailable', True)
