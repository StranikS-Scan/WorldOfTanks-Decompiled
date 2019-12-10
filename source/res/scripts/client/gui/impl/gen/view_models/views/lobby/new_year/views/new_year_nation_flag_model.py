# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_nation_flag_model.py
from frameworks.wulf import ViewModel

class NewYearNationFlagModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NewYearNationFlagModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(0)

    def setNation(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(NewYearNationFlagModel, self)._initialize()
        self._addStringProperty('nation', 'germany')
