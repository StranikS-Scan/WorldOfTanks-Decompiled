# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quest_premium_tab_view_model.py
from gui.impl.gen.view_models.views.lobby.daily.daily_quest_regular_tab_view_model import DailyQuestRegularTabViewModel

class DailyQuestPremiumTabViewModel(DailyQuestRegularTabViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DailyQuestPremiumTabViewModel, self).__init__(properties=properties, commands=commands)

    def getHasPremiumAccount(self):
        return self._getBool(3)

    def setHasPremiumAccount(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(DailyQuestPremiumTabViewModel, self)._initialize()
        self._addBoolProperty('hasPremiumAccount', False)
