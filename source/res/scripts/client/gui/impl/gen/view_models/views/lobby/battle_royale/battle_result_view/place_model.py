# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/place_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.row_model import RowModel

class PlaceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PlaceModel, self).__init__(properties=properties, commands=commands)

    def getPlace(self):
        return self._getString(0)

    def setPlace(self, value):
        self._setString(0, value)

    def getIsSquadMode(self):
        return self._getBool(1)

    def setIsSquadMode(self, value):
        self._setBool(1, value)

    def getPlayersList(self):
        return self._getArray(2)

    def setPlayersList(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(PlaceModel, self)._initialize()
        self._addStringProperty('place', '')
        self._addBoolProperty('isSquadMode', False)
        self._addArrayProperty('playersList', Array())
