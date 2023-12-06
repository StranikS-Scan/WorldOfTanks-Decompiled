# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_collection_bonus_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_collection_table_value_model import NyCollectionTableValueModel

class NyCollectionBonusTooltipModel(ViewModel):
    __slots__ = ()
    NEW_YEAR = 'NewYear'
    XMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'

    def __init__(self, properties=2, commands=0):
        super(NyCollectionBonusTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def collectionsTable(self):
        return self._getViewModel(0)

    @staticmethod
    def getCollectionsTableType():
        return NyCollectionTableValueModel

    def getSelectedCollection(self):
        return self._getString(1)

    def setSelectedCollection(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NyCollectionBonusTooltipModel, self)._initialize()
        self._addViewModelProperty('collectionsTable', UserListModel())
        self._addStringProperty('selectedCollection', 'NewYear')
