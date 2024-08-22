# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/optional_devices_assistant_item.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class OptionalDevicesAssistantItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(OptionalDevicesAssistantItem, self).__init__(properties=properties, commands=commands)

    def getPopularity(self):
        return self._getReal(0)

    def setPopularity(self, value):
        self._setReal(0, value)

    def getItems(self):
        return self._getArray(1)

    def setItems(self, value):
        self._setArray(1, value)

    @staticmethod
    def getItemsType():
        return unicode

    def _initialize(self):
        super(OptionalDevicesAssistantItem, self)._initialize()
        self._addRealProperty('popularity', 0.0)
        self._addArrayProperty('items', Array())
