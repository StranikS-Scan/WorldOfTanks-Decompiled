# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/searching_dropdown_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel

class SearchingDropdownModel(ViewModel):
    __slots__ = ('onOutsideClick',)

    def __init__(self, properties=5, commands=1):
        super(SearchingDropdownModel, self).__init__(properties=properties, commands=commands)

    @property
    def btnCancelSearch(self):
        return self._getViewModel(0)

    def getBackgroundImage(self):
        return self._getString(1)

    def setBackgroundImage(self, value):
        self._setString(1, value)

    def getSeekers(self):
        return self._getNumber(2)

    def setSeekers(self, value):
        self._setNumber(2, value)

    def getSearchStartTime(self):
        return self._getNumber(3)

    def setSearchStartTime(self, value):
        self._setNumber(3, value)

    def getEstimatedTime(self):
        return self._getString(4)

    def setEstimatedTime(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(SearchingDropdownModel, self)._initialize()
        self._addViewModelProperty('btnCancelSearch', ButtonModel())
        self._addStringProperty('backgroundImage', '')
        self._addNumberProperty('seekers', 0)
        self._addNumberProperty('searchStartTime', 0)
        self._addStringProperty('estimatedTime', '')
        self.onOutsideClick = self._addCommand('onOutsideClick')
