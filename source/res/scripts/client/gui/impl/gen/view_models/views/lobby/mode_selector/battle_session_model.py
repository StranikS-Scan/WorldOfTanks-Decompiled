# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/battle_session_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.menu_item_model import MenuItemModel

class BattleSessionModel(ViewModel):
    __slots__ = ('onTournamentsClicked', 'onGlobalMapClicked', 'onClanClicked', 'onCloseClicked', 'onNavigate')

    def __init__(self, properties=7, commands=5):
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

    def getIsTournamentLinkIGB(self):
        return self._getBool(3)

    def setIsTournamentLinkIGB(self, value):
        self._setBool(3, value)

    def getMenuItems(self):
        return self._getArray(4)

    def setMenuItems(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMenuItemsType():
        return MenuItemModel

    def getModeName(self):
        return self._getString(5)

    def setModeName(self, value):
        self._setString(5, value)

    def getModeId(self):
        return self._getString(6)

    def setModeId(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(BattleSessionModel, self)._initialize()
        self._addBoolProperty('isInClan', False)
        self._addStringProperty('clanName', '')
        self._addStringProperty('clanIcon', '')
        self._addBoolProperty('isTournamentLinkIGB', False)
        self._addArrayProperty('menuItems', Array())
        self._addStringProperty('modeName', '')
        self._addStringProperty('modeId', '')
        self.onTournamentsClicked = self._addCommand('onTournamentsClicked')
        self.onGlobalMapClicked = self._addCommand('onGlobalMapClicked')
        self.onClanClicked = self._addCommand('onClanClicked')
        self.onCloseClicked = self._addCommand('onCloseClicked')
        self.onNavigate = self._addCommand('onNavigate')
