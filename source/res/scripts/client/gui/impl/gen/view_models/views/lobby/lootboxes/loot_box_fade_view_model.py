# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_fade_view_model.py
from frameworks.wulf import ViewModel

class LootBoxFadeViewModel(ViewModel):
    __slots__ = ('onFadeInCompleted', 'onWindowClose', 'onCloseClick')

    def __init__(self, properties=3, commands=3):
        super(LootBoxFadeViewModel, self).__init__(properties=properties, commands=commands)

    def getShowWindow(self):
        return self._getBool(0)

    def setShowWindow(self, value):
        self._setBool(0, value)

    def getWithPause(self):
        return self._getBool(1)

    def setWithPause(self, value):
        self._setBool(1, value)

    def getShowError(self):
        return self._getBool(2)

    def setShowError(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(LootBoxFadeViewModel, self)._initialize()
        self._addBoolProperty('showWindow', False)
        self._addBoolProperty('withPause', True)
        self._addBoolProperty('showError', False)
        self.onFadeInCompleted = self._addCommand('onFadeInCompleted')
        self.onWindowClose = self._addCommand('onWindowClose')
        self.onCloseClick = self._addCommand('onCloseClick')
