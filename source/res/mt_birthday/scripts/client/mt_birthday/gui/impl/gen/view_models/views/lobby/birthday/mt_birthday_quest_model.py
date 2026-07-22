# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/mt_birthday_quest_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class QuestStatus(Enum):
    DONE = 'done'
    LOCKED = 'notAvailable'
    DISABLED = 'disabled'
    ACTIVE = 'active'


class MtBirthdayQuestModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(MtBirthdayQuestModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return QuestStatus(self._getString(13))

    def setStatus(self, value):
        self._setString(13, value.value)

    def _initialize(self):
        super(MtBirthdayQuestModel, self)._initialize()
        self._addStringProperty('status')
