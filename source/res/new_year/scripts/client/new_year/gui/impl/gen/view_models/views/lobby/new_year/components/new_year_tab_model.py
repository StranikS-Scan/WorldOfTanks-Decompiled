# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_tab_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MenuNames(Enum):
    CITY = 'city'
    LEADERS = 'leaders'
    MACHINE = 'surprise_machine'
    PET = 'pet'
    INFO = 'info'


class NewYearTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearTabModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return MenuNames(self._getString(0))

    def setName(self, value):
        self._setString(0, value.value)

    def getInfoCount(self):
        return self._getNumber(1)

    def setInfoCount(self, value):
        self._setNumber(1, value)

    def getIconName(self):
        return self._getString(2)

    def setIconName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearTabModel, self)._initialize()
        self._addStringProperty('name')
        self._addNumberProperty('infoCount', 0)
        self._addStringProperty('iconName', '')
