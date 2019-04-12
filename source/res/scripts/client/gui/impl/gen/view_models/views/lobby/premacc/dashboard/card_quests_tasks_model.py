# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/card_quests_tasks_model.py
from frameworks.wulf import ViewModel

class CardQuestsTasksModel(ViewModel):
    __slots__ = ()

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getShowLine(self):
        return self._getBool(1)

    def setShowLine(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(CardQuestsTasksModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addBoolProperty('showLine', False)
