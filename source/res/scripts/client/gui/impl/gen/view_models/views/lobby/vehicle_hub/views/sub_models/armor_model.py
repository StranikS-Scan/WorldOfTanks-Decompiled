# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/armor_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_value_model import ArmorValueModel

class ArmorModel(ViewModel):
    __slots__ = ('onLinkButtonPressed', 'onLegendClicked', 'onLegendTooltipOpened', 'onLegendTooltipClosed')

    def __init__(self, properties=5, commands=4):
        super(ArmorModel, self).__init__(properties=properties, commands=commands)

    def getMainArmor(self):
        return self._getArray(0)

    def setMainArmor(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMainArmorType():
        return ArmorValueModel

    def getSpacedArmor(self):
        return self._getArray(1)

    def setSpacedArmor(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSpacedArmorType():
        return ArmorValueModel

    def getMainGradient(self):
        return self._getResource(2)

    def setMainGradient(self, value):
        self._setResource(2, value)

    def getSpacedGradient(self):
        return self._getResource(3)

    def setSpacedGradient(self, value):
        self._setResource(3, value)

    def getLinkButtonLabel(self):
        return self._getResource(4)

    def setLinkButtonLabel(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(ArmorModel, self)._initialize()
        self._addArrayProperty('mainArmor', Array())
        self._addArrayProperty('spacedArmor', Array())
        self._addResourceProperty('mainGradient', R.invalid())
        self._addResourceProperty('spacedGradient', R.invalid())
        self._addResourceProperty('linkButtonLabel', R.invalid())
        self.onLinkButtonPressed = self._addCommand('onLinkButtonPressed')
        self.onLegendClicked = self._addCommand('onLegendClicked')
        self.onLegendTooltipOpened = self._addCommand('onLegendTooltipOpened')
        self.onLegendTooltipClosed = self._addCommand('onLegendTooltipClosed')
