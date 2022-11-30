# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/challenge/sub_views/challenge_task_switch_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.sub_views.challenge_base_model import ChallengeBaseModel

class TaskSwitchType(Enum):
    SKILL = 'skill'
    DILIGENCE = 'diligence'


class ChallengeTaskSwitchModel(ChallengeBaseModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=2):
        super(ChallengeTaskSwitchModel, self).__init__(properties=properties, commands=commands)

    def getTaskSwitchType(self):
        return self._getString(0)

    def setTaskSwitchType(self, value):
        self._setString(0, value)

    def getErrorMessage(self):
        return self._getString(1)

    def setErrorMessage(self, value):
        self._setString(1, value)

    def getAvailableSwitches(self):
        return self._getNumber(2)

    def setAvailableSwitches(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ChallengeTaskSwitchModel, self)._initialize()
        self._addStringProperty('taskSwitchType', '')
        self._addStringProperty('errorMessage', '')
        self._addNumberProperty('availableSwitches', 0)
