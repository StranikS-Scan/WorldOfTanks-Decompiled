# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/commander_view_model.py
from frameworks.wulf import Array, ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.commander_perk_model import CommanderPerkModel

class CommanderViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CommanderViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    def getNation(self):
        return self._getString(1)

    def setNation(self, value):
        self._setString(1, value)

    def getPerkList(self):
        return self._getArray(2)

    def setPerkList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPerkListType():
        return CommanderPerkModel

    def _initialize(self):
        super(CommanderViewModel, self)._initialize()
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addStringProperty('nation', '')
        self._addArrayProperty('perkList', Array())
