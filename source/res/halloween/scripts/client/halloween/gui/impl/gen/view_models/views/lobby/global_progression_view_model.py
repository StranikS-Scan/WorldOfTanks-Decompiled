# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/global_progression_view_model.py
from frameworks.wulf import Array
from halloween.gui.impl.gen.view_models.views.lobby.common.base_quest_model import BaseQuestModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel

class GlobalProgressionViewModel(BaseViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=1):
        super(GlobalProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsType():
        return BaseQuestModel

    def _initialize(self):
        super(GlobalProgressionViewModel, self)._initialize()
        self._addArrayProperty('quests', Array())
