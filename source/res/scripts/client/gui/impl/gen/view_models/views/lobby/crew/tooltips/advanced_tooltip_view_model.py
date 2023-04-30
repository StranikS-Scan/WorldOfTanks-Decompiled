# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/advanced_tooltip_view_model.py
from frameworks.wulf import ViewModel

class AdvancedTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AdvancedTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getMovie(self):
        return self._getString(0)

    def setMovie(self, value):
        self._setString(0, value)

    def getHeader(self):
        return self._getString(1)

    def setHeader(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(AdvancedTooltipViewModel, self)._initialize()
        self._addStringProperty('movie', '')
        self._addStringProperty('header', '')
        self._addStringProperty('description', '')
