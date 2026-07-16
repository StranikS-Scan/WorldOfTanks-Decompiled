# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/notifications/challenges_start_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class ChallengesStartModel(NotificationBaseModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(ChallengesStartModel, self).__init__(properties=properties, commands=commands)

    def getFirst(self):
        return self._getBool(1)

    def setFirst(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ChallengesStartModel, self)._initialize()
        self._addBoolProperty('first', False)
        self.onClick = self._addCommand('onClick')
