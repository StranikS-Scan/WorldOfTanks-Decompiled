# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/main_menu_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.menu_item_model import MenuItemModel

class MainMenuModel(ViewModel):
    __slots__ = ('onNavigate',)
    MODE_SELECTOR = 'modeSelector'
    SHOP = 'shop'
    STORAGE = 'storage'
    MISSIONS = 'missions'
    PERSONAL_MISSIONS = 'personalMissions'
    ACHIEVEMENTS = 'achievements'
    TECHTREE = 'techtree'
    TOURNAMENT = 'tournament'
    BARRACKS = 'barracks'
    CLANS = 'clans'
    REPLAYS = 'replays'

    def __init__(self, properties=5, commands=1):
        super(MainMenuModel, self).__init__(properties=properties, commands=commands)

    def getMenuItems(self):
        return self._getArray(0)

    def setMenuItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMenuItemsType():
        return MenuItemModel

    def getModeName(self):
        return self._getString(1)

    def setModeName(self, value):
        self._setString(1, value)

    def getModeId(self):
        return self._getString(2)

    def setModeId(self, value):
        self._setString(2, value)

    def getHasTechTreeEvents(self):
        return self._getBool(3)

    def setHasTechTreeEvents(self, value):
        self._setBool(3, value)

    def getClanEmblem(self):
        return self._getString(4)

    def setClanEmblem(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(MainMenuModel, self)._initialize()
        self._addArrayProperty('menuItems', Array())
        self._addStringProperty('modeName', '')
        self._addStringProperty('modeId', '')
        self._addBoolProperty('hasTechTreeEvents', False)
        self._addStringProperty('clanEmblem', '')
        self.onNavigate = self._addCommand('onNavigate')
