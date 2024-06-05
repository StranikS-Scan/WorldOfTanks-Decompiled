# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/live_ops_web_events/entry_point_view_model.py
from gui.impl.gen.view_models.views.lobby.live_ops_web_events.entry_point_base import EntryPointBase

class EntryPointViewModel(EntryPointBase):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(EntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFirstEntry(self):
        return self._getBool(2)

    def setIsFirstEntry(self, value):
        self._setBool(2, value)

    def getIsVisited(self):
        return self._getBool(3)

    def setIsVisited(self, value):
        self._setBool(3, value)

    def getIsSmall(self):
        return self._getBool(4)

    def setIsSmall(self, value):
        self._setBool(4, value)

    def getIsHighQualityPreset(self):
        return self._getBool(5)

    def setIsHighQualityPreset(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(EntryPointViewModel, self)._initialize()
        self._addBoolProperty('isFirstEntry', False)
        self._addBoolProperty('isVisited', False)
        self._addBoolProperty('isSmall', True)
        self._addBoolProperty('isHighQualityPreset', True)
        self.onClick = self._addCommand('onClick')
