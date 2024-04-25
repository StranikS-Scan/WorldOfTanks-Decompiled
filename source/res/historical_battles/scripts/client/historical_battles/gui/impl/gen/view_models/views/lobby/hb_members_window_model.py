# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_members_window_model.py
from frameworks.wulf import Array
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_slot_model import HbSlotModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class HbMembersWindowModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=3):
        super(HbMembersWindowModel, self).__init__(properties=properties, commands=commands)

    def getSlots(self):
        return self._getArray(17)

    def setSlots(self, value):
        self._setArray(17, value)

    @staticmethod
    def getSlotsType():
        return HbSlotModel

    def getIsEvent(self):
        return self._getBool(18)

    def setIsEvent(self, value):
        self._setBool(18, value)

    def getShouldShowInvitePlayersButton(self):
        return self._getBool(19)

    def setShouldShowInvitePlayersButton(self, value):
        self._setBool(19, value)

    def _initialize(self):
        super(HbMembersWindowModel, self)._initialize()
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('isEvent', False)
        self._addBoolProperty('shouldShowInvitePlayersButton', True)
