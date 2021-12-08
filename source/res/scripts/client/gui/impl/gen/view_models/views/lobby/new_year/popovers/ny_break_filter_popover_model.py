# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_break_filter_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_break_filter_button_model import NyBreakFilterButtonModel

class NyBreakFilterPopoverModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onToyTypeSelected', 'onCollectionTypeSelected', 'onAtmosphereBonusSelected')

    def __init__(self, properties=3, commands=4):
        super(NyBreakFilterPopoverModel, self).__init__(properties=properties, commands=commands)

    def getToyTypes(self):
        return self._getArray(0)

    def setToyTypes(self, value):
        self._setArray(0, value)

    def getCollectionTypes(self):
        return self._getArray(1)

    def setCollectionTypes(self, value):
        self._setArray(1, value)

    def getAtmosphereBonuses(self):
        return self._getArray(2)

    def setAtmosphereBonuses(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(NyBreakFilterPopoverModel, self)._initialize()
        self._addArrayProperty('toyTypes', Array())
        self._addArrayProperty('collectionTypes', Array())
        self._addArrayProperty('atmosphereBonuses', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onToyTypeSelected = self._addCommand('onToyTypeSelected')
        self.onCollectionTypeSelected = self._addCommand('onCollectionTypeSelected')
        self.onAtmosphereBonusSelected = self._addCommand('onAtmosphereBonusSelected')
