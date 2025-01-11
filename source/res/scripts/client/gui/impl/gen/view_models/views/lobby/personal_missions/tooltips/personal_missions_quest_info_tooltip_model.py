# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/personal_missions_quest_info_tooltip_model.py
from frameworks.wulf import ViewModel

class PersonalMissionsQuestInfoTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PersonalMissionsQuestInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(PersonalMissionsQuestInfoTooltipModel, self)._initialize()
        self._addStringProperty('type', '')
