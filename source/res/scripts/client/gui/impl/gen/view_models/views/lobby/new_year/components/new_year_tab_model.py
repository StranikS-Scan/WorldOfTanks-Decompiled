# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_tab_model.py
from frameworks.wulf import ViewModel

class NewYearTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NewYearTabModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getUnseenCount(self):
        return self._getNumber(1)

    def setUnseenCount(self, value):
        self._setNumber(1, value)

    def getInfoCount(self):
        return self._getNumber(2)

    def setInfoCount(self, value):
        self._setNumber(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getIsCompleted(self):
        return self._getBool(4)

    def setIsCompleted(self, value):
        self._setBool(4, value)

    def getIsHintVisible(self):
        return self._getBool(5)

    def setIsHintVisible(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NewYearTabModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('unseenCount', 0)
        self._addNumberProperty('infoCount', 0)
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isHintVisible', False)
