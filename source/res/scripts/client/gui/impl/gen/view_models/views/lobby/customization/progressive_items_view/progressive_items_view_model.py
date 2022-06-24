# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progressive_items_view/progressive_items_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_view.item_model import ItemModel
from gui.impl.gen.view_models.views.lobby.customization.progressive_items_view.progression_cases_tutorial_model import ProgressionCasesTutorialModel

class ProgressiveItemsViewModel(ViewModel):
    __slots__ = ('onSelectItem',)

    def __init__(self, properties=7, commands=1):
        super(ProgressiveItemsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progressiveItems(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressiveItemsType():
        return ItemModel

    @property
    def tutorial(self):
        return self._getViewModel(1)

    @staticmethod
    def getTutorialType():
        return ProgressionCasesTutorialModel

    def getTankLevel(self):
        return self._getString(2)

    def setTankLevel(self, value):
        self._setString(2, value)

    def getTankType(self):
        return self._getResource(3)

    def setTankType(self, value):
        self._setResource(3, value)

    def getTankName(self):
        return self._getString(4)

    def setTankName(self, value):
        self._setString(4, value)

    def getIsRendererPipelineDeferred(self):
        return self._getBool(5)

    def setIsRendererPipelineDeferred(self, value):
        self._setBool(5, value)

    def getItemToScroll(self):
        return self._getNumber(6)

    def setItemToScroll(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ProgressiveItemsViewModel, self)._initialize()
        self._addViewModelProperty('progressiveItems', UserListModel())
        self._addViewModelProperty('tutorial', ProgressionCasesTutorialModel())
        self._addStringProperty('tankLevel', '')
        self._addResourceProperty('tankType', R.invalid())
        self._addStringProperty('tankName', '')
        self._addBoolProperty('isRendererPipelineDeferred', False)
        self._addNumberProperty('itemToScroll', 0)
        self.onSelectItem = self._addCommand('onSelectItem')
