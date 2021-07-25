# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/vehicle_card_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class VehicleCardModel(VehicleModel):
    __slots__ = ()
    DEFAULT = 'default'
    SELECTED = 'selected'
    LEARNED = 'learned'
    IN_BATTLE = 'inBattle'
    IN_PLATOON = 'inPlatoon'
    IN_HANGAR = 'inHangar'
    HAS_CREW = 'hasCrew'

    def __init__(self, properties=10, commands=0):
        super(VehicleCardModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return self._getString(8)

    def setStatus(self, value):
        self._setString(8, value)

    def getCardState(self):
        return self._getString(9)

    def setCardState(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(VehicleCardModel, self)._initialize()
        self._addStringProperty('status', '')
        self._addStringProperty('cardState', 'default')
