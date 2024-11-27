# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/quests/ny_quest_entry_point_view_model.py
from frameworks.wulf import ViewModel

class NyQuestEntryPointViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=1, commands=1):
        super(NyQuestEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getQuestsInProgress(self):
        return self._getNumber(0)

    def setQuestsInProgress(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(NyQuestEntryPointViewModel, self)._initialize()
        self._addNumberProperty('questsInProgress', 0)
        self.onAction = self._addCommand('onAction')
