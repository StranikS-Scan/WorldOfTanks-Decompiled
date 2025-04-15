# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/order_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.bundle_model import BundleModel

class OrderViewModel(ViewModel):
    __slots__ = ('onBundleBuyClick', 'onInfoClick')

    def __init__(self, properties=4, commands=2):
        super(OrderViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getCredits(self):
        return self._getNumber(1)

    def setCredits(self, value):
        self._setNumber(1, value)

    def getGold(self):
        return self._getNumber(2)

    def setGold(self, value):
        self._setNumber(2, value)

    def getBundles(self):
        return self._getArray(3)

    def setBundles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBundlesType():
        return BundleModel

    def _initialize(self):
        super(OrderViewModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('gold', 0)
        self._addArrayProperty('bundles', Array())
        self.onBundleBuyClick = self._addCommand('onBundleBuyClick')
        self.onInfoClick = self._addCommand('onInfoClick')
