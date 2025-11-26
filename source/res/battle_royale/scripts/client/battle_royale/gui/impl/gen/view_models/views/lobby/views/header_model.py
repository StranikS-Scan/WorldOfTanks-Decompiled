# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/header_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ModeStatus(Enum):
    ALERT = 'alert'
    BATTLESELECTOR = 'battleSelector'


class HeaderModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(HeaderModel, self).__init__(properties=properties, commands=commands)

    def getModeStatus(self):
        return ModeStatus(self._getString(0))

    def setModeStatus(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(HeaderModel, self)._initialize()
        self._addStringProperty('modeStatus', ModeStatus.BATTLESELECTOR.value)
