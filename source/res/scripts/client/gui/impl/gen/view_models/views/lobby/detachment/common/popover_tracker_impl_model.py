# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/popover_tracker_impl_model.py
from frameworks.wulf import ViewModel

class PopoverTrackerImplModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PopoverTrackerImplModel, self).__init__(properties=properties, commands=commands)

    def getIsActive(self):
        return self._getBool(0)

    def setIsActive(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(PopoverTrackerImplModel, self)._initialize()
        self._addBoolProperty('isActive', False)
