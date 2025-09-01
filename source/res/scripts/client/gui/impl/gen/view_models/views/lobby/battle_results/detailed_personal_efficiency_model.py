# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/detailed_personal_efficiency_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel

class DetailedPersonalEfficiencyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DetailedPersonalEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getDatabaseID(self):
        return self._getNumber(0)

    def setDatabaseID(self, value):
        self._setNumber(0, value)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getPersonalEfficiencyItems(self):
        return self._getArray(2)

    def setPersonalEfficiencyItems(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPersonalEfficiencyItemsType():
        return DetailedPersonalEfficiencyItemModel

    def _initialize(self):
        super(DetailedPersonalEfficiencyModel, self)._initialize()
        self._addNumberProperty('databaseID', 0)
        self._addStringProperty('userName', '0')
        self._addArrayProperty('personalEfficiencyItems', Array())
