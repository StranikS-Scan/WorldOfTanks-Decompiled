# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/season_point_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName, SeasonPointState
from frameworks.wulf import ViewModel

class SeasonPointModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SeasonPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return SeasonPointState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getSeason(self):
        return SeasonName(self._getString(1))

    def setSeason(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(SeasonPointModel, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('season')
