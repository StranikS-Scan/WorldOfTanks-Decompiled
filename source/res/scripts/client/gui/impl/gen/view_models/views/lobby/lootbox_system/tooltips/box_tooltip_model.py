# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/box_tooltip_model.py
from frameworks.wulf import ViewModel

class BoxTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BoxTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getBoxesCountToGuaranteed(self):
        return self._getNumber(1)

    def setBoxesCountToGuaranteed(self, value):
        self._setNumber(1, value)

    def getBoxCategory(self):
        return self._getString(2)

    def setBoxCategory(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BoxTooltipModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addNumberProperty('boxesCountToGuaranteed', 0)
        self._addStringProperty('boxCategory', '')
