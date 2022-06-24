# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/bonuses_event_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.marathon.base_event_model import BaseEventModel

class BonusesEventModel(BaseEventModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=1):
        super(BonusesEventModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(BonusesEventModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
