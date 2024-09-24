# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/box_info_model.py
from frameworks.wulf import ViewModel

class BoxInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BoxInfoModel, self).__init__(properties=properties, commands=commands)

    def getBoxCategory(self):
        return self._getString(0)

    def setBoxCategory(self, value):
        self._setString(0, value)

    def getBoxesCount(self):
        return self._getNumber(1)

    def setBoxesCount(self, value):
        self._setNumber(1, value)

    def getBoxesCountToGuaranteed(self):
        return self._getNumber(2)

    def setBoxesCountToGuaranteed(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BoxInfoModel, self)._initialize()
        self._addStringProperty('boxCategory', '')
        self._addNumberProperty('boxesCount', 0)
        self._addNumberProperty('boxesCountToGuaranteed', 0)
