# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_slot_model.py
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel

class PortalSlotModel(SlotModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(PortalSlotModel, self).__init__(properties=properties, commands=commands)

    def getMaxComplexity(self):
        return self._getNumber(12)

    def setMaxComplexity(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(PortalSlotModel, self)._initialize()
        self._addNumberProperty('maxComplexity', 0)
