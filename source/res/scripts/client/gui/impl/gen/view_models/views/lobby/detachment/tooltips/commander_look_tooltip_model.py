# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/commander_look_tooltip_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_model import CommanderModel

class CommanderLookTooltipModel(CommanderModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(CommanderLookTooltipModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getResource(6)

    def setDescription(self, value):
        self._setResource(6, value)

    def getRarity(self):
        return self._getResource(7)

    def setRarity(self, value):
        self._setResource(7, value)

    def getUseCount(self):
        return self._getNumber(8)

    def setUseCount(self, value):
        self._setNumber(8, value)

    def getFreeCount(self):
        return self._getNumber(9)

    def setFreeCount(self, value):
        self._setNumber(9, value)

    def getUsedIn(self):
        return self._getString(10)

    def setUsedIn(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(CommanderLookTooltipModel, self)._initialize()
        self._addResourceProperty('description', R.invalid())
        self._addResourceProperty('rarity', R.invalid())
        self._addNumberProperty('useCount', 0)
        self._addNumberProperty('freeCount', 0)
        self._addStringProperty('usedIn', '')
