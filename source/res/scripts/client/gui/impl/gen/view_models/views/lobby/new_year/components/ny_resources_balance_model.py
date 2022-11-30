# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_resources_balance_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel

class CollectState(Enum):
    AVAILABLE = 'available'
    COLLECTED = 'collected'
    AUTOCOLLECT = 'autoCollect'


class NyResourcesBalanceModel(ViewModel):
    __slots__ = ('onCollectResources', 'onConvertResources', 'onGoToResources')

    def __init__(self, properties=5, commands=3):
        super(NyResourcesBalanceModel, self).__init__(properties=properties, commands=commands)

    def getCollectCooldown(self):
        return self._getNumber(0)

    def setCollectCooldown(self, value):
        self._setNumber(0, value)

    def getCollectState(self):
        return CollectState(self._getString(1))

    def setCollectState(self, value):
        self._setString(1, value.value)

    def getIsResourcesTabOpen(self):
        return self._getBool(2)

    def setIsResourcesTabOpen(self, value):
        self._setBool(2, value)

    def getIsWalletAvailable(self):
        return self._getBool(3)

    def setIsWalletAvailable(self, value):
        self._setBool(3, value)

    def getResources(self):
        return self._getArray(4)

    def setResources(self, value):
        self._setArray(4, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def _initialize(self):
        super(NyResourcesBalanceModel, self)._initialize()
        self._addNumberProperty('collectCooldown', 0)
        self._addStringProperty('collectState')
        self._addBoolProperty('isResourcesTabOpen', False)
        self._addBoolProperty('isWalletAvailable', False)
        self._addArrayProperty('resources', Array())
        self.onCollectResources = self._addCommand('onCollectResources')
        self.onConvertResources = self._addCommand('onConvertResources')
        self.onGoToResources = self._addCommand('onGoToResources')
