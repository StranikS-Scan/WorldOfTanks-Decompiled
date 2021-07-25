# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/presentation_crew_subheader_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PresentationCrewSubheaderTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PresentationCrewSubheaderTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(PresentationCrewSubheaderTooltipModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addResourceProperty('icon', R.invalid())
