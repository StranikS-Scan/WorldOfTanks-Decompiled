# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_break_filter_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_break_filter_button_model import NyBreakFilterButtonModel

class NyBreakFilterPopoverModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onToyTypeSelected', 'onCollectionTypeSelected', 'onToyRankSelected')

    def __init__(self, properties=3, commands=4):
        super(NyBreakFilterPopoverModel, self).__init__(properties=properties, commands=commands)

    def getToyTypes(self):
        return self._getArray(0)

    def setToyTypes(self, value):
        self._setArray(0, value)

    @staticmethod
    def getToyTypesType():
        return NyBreakFilterButtonModel

    def getCollectionTypes(self):
        return self._getArray(1)

    def setCollectionTypes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCollectionTypesType():
        return NyBreakFilterButtonModel

    def getToyRanks(self):
        return self._getArray(2)

    def setToyRanks(self, value):
        self._setArray(2, value)

    @staticmethod
    def getToyRanksType():
        return NyBreakFilterButtonModel

    def _initialize(self):
        super(NyBreakFilterPopoverModel, self)._initialize()
        self._addArrayProperty('toyTypes', Array())
        self._addArrayProperty('collectionTypes', Array())
        self._addArrayProperty('toyRanks', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onToyTypeSelected = self._addCommand('onToyTypeSelected')
        self.onCollectionTypeSelected = self._addCommand('onCollectionTypeSelected')
        self.onToyRankSelected = self._addCommand('onToyRankSelected')
