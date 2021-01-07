# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/tier_button_model.py
from frameworks.wulf import ViewModel

class TierButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TierButtonModel, self).__init__(properties=properties, commands=commands)

    def getTier(self):
        return self._getNumber(0)

    def setTier(self, value):
        self._setNumber(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(TierButtonModel, self)._initialize()
        self._addNumberProperty('tier', 0)
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('isSelected', False)
