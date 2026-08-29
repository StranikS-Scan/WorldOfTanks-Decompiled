# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/commander_cmp_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.battle_royale.commander_cmp_perk_model import CommanderCmpPerkModel

class CommanderCmpViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CommanderCmpViewModel, self).__init__(properties=properties, commands=commands)

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
        return CommanderCmpPerkModel

    def _initialize(self):
        super(CommanderCmpViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addArrayProperty('perkList', Array())
