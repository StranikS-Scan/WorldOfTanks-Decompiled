# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/feature_tooltip_view_model.py
from frameworks.wulf import ViewModel

class FeatureTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FeatureTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsUnlocked(self):
        return self._getBool(0)

    def setIsUnlocked(self, value):
        self._setBool(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(FeatureTooltipViewModel, self)._initialize()
        self._addBoolProperty('isUnlocked', False)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isDisabled', False)
