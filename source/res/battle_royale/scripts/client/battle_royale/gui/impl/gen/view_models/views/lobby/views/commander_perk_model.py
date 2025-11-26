# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/commander_perk_model.py
from frameworks.wulf import ViewModel

class CommanderPerkModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CommanderPerkModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getTooltipID(self):
        return self._getString(1)

    def setTooltipID(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(CommanderPerkModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('tooltipID', '')
