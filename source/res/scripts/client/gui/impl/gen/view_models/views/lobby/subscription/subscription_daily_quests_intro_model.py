# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/subscription/subscription_daily_quests_intro_model.py
from frameworks.wulf import ViewModel

class SubscriptionDailyQuestsIntroModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(SubscriptionDailyQuestsIntroModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(SubscriptionDailyQuestsIntroModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
