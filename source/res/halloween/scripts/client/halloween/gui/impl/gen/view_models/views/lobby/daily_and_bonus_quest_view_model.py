# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/daily_and_bonus_quest_view_model.py
from halloween.gui.impl.gen.view_models.views.lobby.bonus_quest_model import BonusQuestModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
from halloween.gui.impl.gen.view_models.views.lobby.daily_quest_model import DailyQuestModel
from halloween.gui.impl.gen.view_models.views.lobby.shop_card_model import ShopCardModel

class DailyAndBonusQuestViewModel(BaseViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=1):
        super(DailyAndBonusQuestViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def dailyQuestModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getDailyQuestModelType():
        return DailyQuestModel

    @property
    def bonusQuestModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getBonusQuestModelType():
        return BonusQuestModel

    @property
    def shopCardModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getShopCardModelType():
        return ShopCardModel

    def _initialize(self):
        super(DailyAndBonusQuestViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuestModel', DailyQuestModel())
        self._addViewModelProperty('bonusQuestModel', BonusQuestModel())
        self._addViewModelProperty('shopCardModel', ShopCardModel())
