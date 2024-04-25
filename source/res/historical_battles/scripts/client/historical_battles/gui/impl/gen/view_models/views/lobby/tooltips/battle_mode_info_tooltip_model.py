# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/battle_mode_info_tooltip_model.py
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_mode_model import BattleModeModel

class BattleModeInfoTooltipModel(BattleModeModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BattleModeInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFrontStartTimestamp(self):
        return self._getNumber(4)

    def setFrontStartTimestamp(self, value):
        self._setNumber(4, value)

    def getEventEndTimestamp(self):
        return self._getNumber(5)

    def setEventEndTimestamp(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(BattleModeInfoTooltipModel, self)._initialize()
        self._addNumberProperty('frontStartTimestamp', 0)
        self._addNumberProperty('eventEndTimestamp', 0)
