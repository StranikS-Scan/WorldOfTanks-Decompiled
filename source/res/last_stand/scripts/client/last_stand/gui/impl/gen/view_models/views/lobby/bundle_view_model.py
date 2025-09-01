# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/bundle_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
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

    def __init__(self, properties=6, commands=2):
        super(BundleViewModel, self).__init__(properties=properties, commands=commands)

    def getLackOfKeys(self):
        return self._getNumber(0)

    def setLackOfKeys(self, value):
        self._setNumber(0, value)

    def getSlide(self):
        return self._getNumber(1)

    def setSlide(self, value):
        self._setNumber(1, value)

    def getWindowType(self):
        return WindowType(self._getString(2))

    def setWindowType(self, value):
        self._setString(2, value.value)

    def getTitleState(self):
        return TitleStates(self._getString(3))

    def setTitleState(self, value):
        self._setString(3, value.value)

    def getBundles(self):
        return self._getArray(4)

    def setBundles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBundlesType():
        return BundleModel

    def getGoldCount(self):
        return self._getNumber(5)

    def setGoldCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(BundleViewModel, self)._initialize()
        self._addNumberProperty('lackOfKeys', 0)
        self._addNumberProperty('slide', 0)
        self._addStringProperty('windowType')
        self._addStringProperty('titleState')
        self._addArrayProperty('bundles', Array())
        self._addNumberProperty('goldCount', 0)
        self.onClose = self._addCommand('onClose')
        self.onPurchase = self._addCommand('onPurchase')
