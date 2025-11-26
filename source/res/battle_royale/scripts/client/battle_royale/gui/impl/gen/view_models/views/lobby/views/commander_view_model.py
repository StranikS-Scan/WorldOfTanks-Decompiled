# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/commander_view_model.py
from frameworks.wulf import Array, ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.commander_perk_model import CommanderPerkModel

class CommanderViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CommanderViewModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(0)

    def setNation(self, value):
        self._setString(0, value)

    def getPerkList(self):
        return self._getArray(1)

    def setPerkList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPerkListType():
        return CommanderPerkModel

    def _initialize(self):
        super(CommanderViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addArrayProperty('perkList', Array())
