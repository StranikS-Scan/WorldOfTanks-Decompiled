# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/quests/ny_quest_card_model.py
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class NyQuestCardModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NyQuestCardModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(11)

    def setIcon(self, value):
        self._setString(11, value)

    def getIsNew(self):
        return self._getBool(12)

    def setIsNew(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NyQuestCardModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addBoolProperty('isNew', True)
