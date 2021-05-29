# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/battle_session_model.py
from frameworks.wulf import ViewModel

class BattleSessionModel(ViewModel):
    __slots__ = ('onTournamentsClicked', 'onGlobalMapClicked', 'onClanClicked', 'onCloseClicked')

    def __init__(self, properties=4, commands=4):
        super(BattleSessionModel, self).__init__(properties=properties, commands=commands)

    def getIsInClan(self):
        return self._getBool(0)

    def setIsInClan(self, value):
        self._setBool(0, value)

    def getClanName(self):
        return self._getString(1)

    def setClanName(self, value):
        self._setString(1, value)

    def getClanIcon(self):
        return self._getString(2)

    def setClanIcon(self, value):
        self._setString(2, value)

    def getIsChina(self):
        return self._getBool(3)

    def setIsChina(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BattleSessionModel, self)._initialize()
        self._addBoolProperty('isInClan', False)
        self._addStringProperty('clanName', '')
        self._addStringProperty('clanIcon', '')
        self._addBoolProperty('isChina', False)
        self.onTournamentsClicked = self._addCommand('onTournamentsClicked')
        self.onGlobalMapClicked = self._addCommand('onGlobalMapClicked')
        self.onClanClicked = self._addCommand('onClanClicked')
        self.onCloseClicked = self._addCommand('onCloseClicked')
