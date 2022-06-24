# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/pre_battle_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.team_model import TeamModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.user_extended_model import UserExtendedModel
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem

class PreBattleViewModel(ViewModel):
    __slots__ = ('onBattleClick', 'onClose')

    def __init__(self, properties=5, commands=2):
        super(PreBattleViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getIsSpectator(self):
        return self._getBool(1)

    def setIsSpectator(self, value):
        self._setBool(1, value)

    def getTeams(self):
        return self._getArray(2)

    def setTeams(self, value):
        self._setArray(2, value)

    @staticmethod
    def getTeamsType():
        return TeamModel

    def getCurrentTeam(self):
        return self._getArray(3)

    def setCurrentTeam(self, value):
        self._setArray(3, value)

    @staticmethod
    def getCurrentTeamType():
        return UserExtendedModel

    def getMaps(self):
        return self._getArray(4)

    def setMaps(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMapsType():
        return GfDropDownItem

    def _initialize(self):
        super(PreBattleViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addBoolProperty('isSpectator', False)
        self._addArrayProperty('teams', Array())
        self._addArrayProperty('currentTeam', Array())
        self._addArrayProperty('maps', Array())
        self.onBattleClick = self._addCommand('onBattleClick')
        self.onClose = self._addCommand('onClose')
