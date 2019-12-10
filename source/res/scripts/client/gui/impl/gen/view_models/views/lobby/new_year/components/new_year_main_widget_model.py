# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_main_widget_model.py
from frameworks.wulf import ViewModel

class NewYearMainWidgetModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=6, commands=1):
        super(NewYearMainWidgetModel, self).__init__(properties=properties, commands=commands)

    def getAnimationType(self):
        return self._getString(0)

    def setAnimationType(self, value):
        self._setString(0, value)

    def getLobbyMode(self):
        return self._getBool(1)

    def setLobbyMode(self, value):
        self._setBool(1, value)

    def getUserLanguage(self):
        return self._getString(2)

    def setUserLanguage(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getLevelRoman(self):
        return self._getString(4)

    def setLevelRoman(self, value):
        self._setString(4, value)

    def getIsExtendedAnim(self):
        return self._getBool(5)

    def setIsExtendedAnim(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NewYearMainWidgetModel, self)._initialize()
        self._addStringProperty('animationType', 'none')
        self._addBoolProperty('lobbyMode', True)
        self._addStringProperty('userLanguage', '')
        self._addNumberProperty('level', 1)
        self._addStringProperty('levelRoman', '')
        self._addBoolProperty('isExtendedAnim', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
