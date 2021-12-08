# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_mega_device_model.py
from frameworks.wulf import ViewModel

class NyCraftMegaDeviceModel(ViewModel):
    __slots__ = ('onToggleChanged',)

    def __init__(self, properties=2, commands=1):
        super(NyCraftMegaDeviceModel, self).__init__(properties=properties, commands=commands)

    def getCollectedToys(self):
        return self._getNumber(0)

    def setCollectedToys(self, value):
        self._setNumber(0, value)

    def getEnabled(self):
        return self._getBool(1)

    def setEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyCraftMegaDeviceModel, self)._initialize()
        self._addNumberProperty('collectedToys', 0)
        self._addBoolProperty('enabled', False)
        self.onToggleChanged = self._addCommand('onToggleChanged')
