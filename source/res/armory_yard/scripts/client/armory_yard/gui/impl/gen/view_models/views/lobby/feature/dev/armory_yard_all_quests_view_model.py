# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/dev/armory_yard_all_quests_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_quest_sub_model import ArmoryYardQuestSubModel

class ArmoryYardAllQuestsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ArmoryYardAllQuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return ArmoryYardQuestSubModel

    def _initialize(self):
        super(ArmoryYardAllQuestsViewModel, self)._initialize()
        self._addArrayProperty('quests', Array())
