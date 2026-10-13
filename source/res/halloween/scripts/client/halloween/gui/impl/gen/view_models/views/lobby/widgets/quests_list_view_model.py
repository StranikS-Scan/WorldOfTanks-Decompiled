# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/widgets/quests_list_view_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.quests_card_view_model import QuestsCardViewModel

class QuestsListViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=1, commands=1):
        super(QuestsListViewModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return QuestsCardViewModel

    def _initialize(self):
        super(QuestsListViewModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self.onClick = self._addCommand('onClick')
