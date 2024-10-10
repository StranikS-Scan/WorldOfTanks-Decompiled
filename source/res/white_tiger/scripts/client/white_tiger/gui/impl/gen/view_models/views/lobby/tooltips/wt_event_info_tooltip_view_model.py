# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_event_info_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtEventInfoTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WtEventInfoTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getInfo(self):
        return self._getResource(2)

    def setInfo(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(WtEventInfoTooltipViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addResourceProperty('info', R.invalid())
