# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/presentation_instructions_subheader_tooltip_model.py
from frameworks.wulf import ViewModel

class PresentationInstructionsSubheaderTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PresentationInstructionsSubheaderTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(PresentationInstructionsSubheaderTooltipModel, self)._initialize()
        self._addNumberProperty('count', 0)
