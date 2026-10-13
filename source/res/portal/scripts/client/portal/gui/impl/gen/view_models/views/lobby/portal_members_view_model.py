# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_members_view_model.py
from frameworks.wulf import Array
from portal.gui.impl.gen.view_models.views.lobby.portal_slot_model import PortalSlotModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class PortalMembersViewModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=3):
        super(PortalMembersViewModel, self).__init__(properties=properties, commands=commands)

    def getComplexity(self):
        return self._getNumber(17)

    def setComplexity(self, value):
        self._setNumber(17, value)

    def getSlots(self):
        return self._getArray(18)

    def setSlots(self, value):
        self._setArray(18, value)

    @staticmethod
    def getSlotsType():
        return PortalSlotModel

    def _initialize(self):
        super(PortalMembersViewModel, self)._initialize()
        self._addNumberProperty('complexity', 0)
        self._addArrayProperty('slots', Array())
