# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/rank_rewards_model.py
from frameworks.wulf import Array
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.rank_rewards_item_model import RankRewardsItemModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_base_model import ProgressionBaseModel
from comp7.gui.impl.gen.view_models.views.lobby.qualification_model import QualificationModel

class RankRewardsModel(ProgressionBaseModel):
    __slots__ = ('onPreviewOpen',)
    DEFAULT_ITEM_INDEX = -1

    def __init__(self, properties=5, commands=1):
        super(RankRewardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def qualificationModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getQualificationModelType():
        return QualificationModel

    def getItems(self):
        return self._getArray(3)

    def setItems(self, value):
        self._setArray(3, value)

    @staticmethod
    def getItemsType():
        return RankRewardsItemModel

    def getInitialItemIndex(self):
        return self._getNumber(4)

    def setInitialItemIndex(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(RankRewardsModel, self)._initialize()
        self._addViewModelProperty('qualificationModel', QualificationModel())
        self._addArrayProperty('items', Array())
        self._addNumberProperty('initialItemIndex', -1)
        self.onPreviewOpen = self._addCommand('onPreviewOpen')
