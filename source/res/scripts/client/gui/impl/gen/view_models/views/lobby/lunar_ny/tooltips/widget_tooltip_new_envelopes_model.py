# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/tooltips/widget_tooltip_new_envelopes_model.py
from frameworks.wulf import ViewModel

class WidgetTooltipNewEnvelopesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WidgetTooltipNewEnvelopesModel, self).__init__(properties=properties, commands=commands)

    def getSecretSantaSentLimitTime(self):
        return self._getNumber(0)

    def setSecretSantaSentLimitTime(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(WidgetTooltipNewEnvelopesModel, self)._initialize()
        self._addNumberProperty('secretSantaSentLimitTime', 0)
