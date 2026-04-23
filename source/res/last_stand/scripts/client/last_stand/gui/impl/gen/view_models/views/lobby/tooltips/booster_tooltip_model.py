# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/booster_tooltip_model.py
from frameworks.wulf import ViewModel

class BoosterTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BoosterTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBooster(self):
        return self._getString(0)

    def setBooster(self, value):
        self._setString(0, value)

    def getBody(self):
        return self._getString(1)

    def setBody(self, value):
        self._setString(1, value)

    def getActivated(self):
        return self._getBool(2)

    def setActivated(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BoosterTooltipModel, self)._initialize()
        self._addStringProperty('booster', '')
        self._addStringProperty('body', '')
        self._addBoolProperty('activated', False)
