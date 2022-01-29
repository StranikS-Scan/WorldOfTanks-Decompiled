# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/tooltips/widget_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.progression_model import ProgressionModel

class WidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def envelopesProgression(self):
        return self._getViewModel(0)

    def getEventTimeLeft(self):
        return self._getNumber(1)

    def setEventTimeLeft(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('envelopesProgression', ProgressionModel())
        self._addNumberProperty('eventTimeLeft', 0)
