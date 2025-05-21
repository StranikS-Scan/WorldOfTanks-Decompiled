# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/bundle_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.bundle_model import BundleModel

class WindowType(Enum):
    KEYWIDGET = 'keyWidget'
    DECRYPT = 'decrypt'
    SKIP = 'skip'


class TitleStates(Enum):
    DEFAULT = 'default'
    ONLYSHOPBUNDLE = 'onlyShopBundle'
    ONLYKEYSBUNDLE = 'onlyKeysBundle'


class BundleViewModel(ViewModel):
    __slots__ = ('onClose', 'onPurchase')

    def __init__(self, properties=5, commands=2):
        super(BundleViewModel, self).__init__(properties=properties, commands=commands)

    def getLackOfKeys(self):
        return self._getNumber(0)

    def setLackOfKeys(self, value):
        self._setNumber(0, value)

    def getWindowType(self):
        return WindowType(self._getString(1))

    def setWindowType(self, value):
        self._setString(1, value.value)

    def getTitleState(self):
        return TitleStates(self._getString(2))

    def setTitleState(self, value):
        self._setString(2, value.value)

    def getBundles(self):
        return self._getArray(3)

    def setBundles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBundlesType():
        return BundleModel

    def getGoldCount(self):
        return self._getNumber(4)

    def setGoldCount(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(BundleViewModel, self)._initialize()
        self._addNumberProperty('lackOfKeys', 0)
        self._addStringProperty('windowType')
        self._addStringProperty('titleState')
        self._addArrayProperty('bundles', Array())
        self._addNumberProperty('goldCount', 0)
        self.onClose = self._addCommand('onClose')
        self.onPurchase = self._addCommand('onPurchase')
