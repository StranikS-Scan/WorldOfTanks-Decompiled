# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/premium_mission_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class PremiumMissionModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(PremiumMissionModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(11)

    def setIcon(self, value):
        self._setString(11, value)

    def getSubscriptionBonuses(self):
        return self._getArray(12)

    def setSubscriptionBonuses(self, value):
        self._setArray(12, value)

    @staticmethod
    def getSubscriptionBonusesType():
        return BonusModel

    def getIsEnabledSubscription(self):
        return self._getBool(13)

    def setIsEnabledSubscription(self, value):
        self._setBool(13, value)

    def getIsActiveSubscription(self):
        return self._getBool(14)

    def setIsActiveSubscription(self, value):
        self._setBool(14, value)

    def getIsFirstView(self):
        return self._getBool(15)

    def setIsFirstView(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(PremiumMissionModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addArrayProperty('subscriptionBonuses', Array())
        self._addBoolProperty('isEnabledSubscription', False)
        self._addBoolProperty('isActiveSubscription', False)
        self._addBoolProperty('isFirstView', False)
