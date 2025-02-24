# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_quest_reset_view_model.py
from frameworks.wulf import ViewModel

class PersonalMissionsQuestResetViewModel(ViewModel):
    __slots__ = ('onConfirm', 'onClose')

    def __init__(self, properties=1, commands=2):
        super(PersonalMissionsQuestResetViewModel, self).__init__(properties=properties, commands=commands)

    def getQuestName(self):
        return self._getString(0)

    def setQuestName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(PersonalMissionsQuestResetViewModel, self)._initialize()
        self._addStringProperty('questName', '')
        self.onConfirm = self._addCommand('onConfirm')
        self.onClose = self._addCommand('onClose')
