# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class HangarViewModel(RouterModel):
    __slots__ = ('onAboutClick', 'onViewLoaded', 'onNarrationClick')

    def __init__(self, properties=7, commands=5):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    def getIsInfoEnabled(self):
        return self._getBool(2)

    def setIsInfoEnabled(self, value):
        self._setBool(2, value)

    def getIsLootBoxEntryPointEnabled(self):
        return self._getBool(3)

    def setIsLootBoxEntryPointEnabled(self, value):
        self._setBool(3, value)

    def getIsLoadedSetup(self):
        return self._getBool(4)

    def setIsLoadedSetup(self, value):
        self._setBool(4, value)

    def getSelectedStory(self):
        return self._getNumber(5)

    def setSelectedStory(self, value):
        self._setNumber(5, value)

    def getShowDailyAnim(self):
        return self._getBool(6)

    def setShowDailyAnim(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addBoolProperty('isInfoEnabled', False)
        self._addBoolProperty('isLootBoxEntryPointEnabled', False)
        self._addBoolProperty('isLoadedSetup', False)
        self._addNumberProperty('selectedStory', 0)
        self._addBoolProperty('showDailyAnim', False)
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onNarrationClick = self._addCommand('onNarrationClick')
