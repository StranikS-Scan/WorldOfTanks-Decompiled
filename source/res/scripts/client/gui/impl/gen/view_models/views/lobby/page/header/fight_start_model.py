# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/fight_start_model.py
from frameworks.wulf import ViewModel

class FightStartModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FightStartModel, self).__init__(properties=properties, commands=commands)

    def getTooltip(self):
        return self._getString(0)

    def setTooltip(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(FightStartModel, self)._initialize()
        self._addStringProperty('tooltip', '')
