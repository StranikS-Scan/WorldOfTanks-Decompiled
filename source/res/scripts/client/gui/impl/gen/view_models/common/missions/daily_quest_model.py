# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/daily_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class DailyQuestModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(DailyQuestModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(13)

    def setIcon(self, value):
        self._setString(13, value)

    def getSubscriptionBonuses(self):
        return self._getArray(14)

    def setSubscriptionBonuses(self, value):
        self._setArray(14, value)

    @staticmethod
    def getSubscriptionBonusesType():
        return BonusModel

    def getIsEnabledSubscription(self):
        return self._getBool(15)

    def setIsEnabledSubscription(self, value):
        self._setBool(15, value)

    def getIsActiveSubscription(self):
        return self._getBool(16)

    def setIsActiveSubscription(self, value):
        self._setBool(16, value)

    def getIsFirstView(self):
        return self._getBool(17)

    def setIsFirstView(self, value):
        self._setBool(17, value)

    def getHasPremium(self):
        return self._getBool(18)

    def setHasPremium(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(DailyQuestModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addArrayProperty('subscriptionBonuses', Array())
        self._addBoolProperty('isEnabledSubscription', False)
        self._addBoolProperty('isActiveSubscription', False)
        self._addBoolProperty('isFirstView', False)
        self._addBoolProperty('hasPremium', False)
