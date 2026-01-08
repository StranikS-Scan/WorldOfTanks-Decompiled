# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/stronghold/stronghold_main_widget_model.py
from frameworks.wulf import ViewModel

class StrongholdMainWidgetModel(ViewModel):
    __slots__ = ('onOpenStrongholdEventProgression',)

    def __init__(self, properties=3, commands=1):
        super(StrongholdMainWidgetModel, self).__init__(properties=properties, commands=commands)

    def getProgressionLevel(self):
        return self._getNumber(0)

    def setProgressionLevel(self, value):
        self._setNumber(0, value)

    def getIsInClan(self):
        return self._getBool(1)

    def setIsInClan(self, value):
        self._setBool(1, value)

    def getIsActive(self):
        return self._getBool(2)

    def setIsActive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(StrongholdMainWidgetModel, self)._initialize()
        self._addNumberProperty('progressionLevel', 0)
        self._addBoolProperty('isInClan', False)
        self._addBoolProperty('isActive', False)
        self.onOpenStrongholdEventProgression = self._addCommand('onOpenStrongholdEventProgression')
