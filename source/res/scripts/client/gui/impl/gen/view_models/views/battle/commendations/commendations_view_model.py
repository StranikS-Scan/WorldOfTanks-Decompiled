# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/commendations/commendations_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle.commendations.player_model import PlayerModel

class CommendationsViewModel(ViewModel):
    __slots__ = ('onExitBattle', 'onClose', 'onCommend', 'onReport', 'onSettingsClick')

    def __init__(self, properties=5, commands=5):
        super(CommendationsViewModel, self).__init__(properties=properties, commands=commands)

    def getAllies(self):
        return self._getArray(0)

    def setAllies(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAlliesType():
        return PlayerModel

    def getTotalReportAmount(self):
        return self._getNumber(1)

    def setTotalReportAmount(self, value):
        self._setNumber(1, value)

    def getReportAmountLeft(self):
        return self._getNumber(2)

    def setReportAmountLeft(self, value):
        self._setNumber(2, value)

    def getMapName(self):
        return self._getString(3)

    def setMapName(self, value):
        self._setString(3, value)

    def getMapType(self):
        return self._getString(4)

    def setMapType(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(CommendationsViewModel, self)._initialize()
        self._addArrayProperty('allies', Array())
        self._addNumberProperty('totalReportAmount', 3)
        self._addNumberProperty('reportAmountLeft', 3)
        self._addStringProperty('mapName', '')
        self._addStringProperty('mapType', '')
        self.onExitBattle = self._addCommand('onExitBattle')
        self.onClose = self._addCommand('onClose')
        self.onCommend = self._addCommand('onCommend')
        self.onReport = self._addCommand('onReport')
        self.onSettingsClick = self._addCommand('onSettingsClick')
