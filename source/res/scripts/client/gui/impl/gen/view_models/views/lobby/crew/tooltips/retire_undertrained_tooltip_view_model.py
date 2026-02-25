# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/retire_undertrained_tooltip_view_model.py
from frameworks.wulf import ViewModel

class RetireUndertrainedTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RetireUndertrainedTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getHasUndertrainedCrewMembers(self):
        return self._getBool(0)

    def setHasUndertrainedCrewMembers(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(RetireUndertrainedTooltipViewModel, self)._initialize()
        self._addBoolProperty('hasUndertrainedCrewMembers', False)
