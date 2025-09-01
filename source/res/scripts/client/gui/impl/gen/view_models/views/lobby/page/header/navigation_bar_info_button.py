# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/navigation_bar_info_button.py
from enum import Enum
from frameworks.wulf import ViewModel

class ButtonType(Enum):
    INFO = 'Info'
    QUESTION = 'Question'
    VIDEO = 'Video'


class NavigationBarInfoButton(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NavigationBarInfoButton, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getString(0)

    def setLabel(self, value):
        self._setString(0, value)

    def getTooltipHeader(self):
        return self._getString(1)

    def setTooltipHeader(self, value):
        self._setString(1, value)

    def getTooltipBody(self):
        return self._getString(2)

    def setTooltipBody(self, value):
        self._setString(2, value)

    def getType(self):
        return ButtonType(self._getString(3))

    def setType(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(NavigationBarInfoButton, self)._initialize()
        self._addStringProperty('label', '')
        self._addStringProperty('tooltipHeader', '')
        self._addStringProperty('tooltipBody', '')
        self._addStringProperty('type', ButtonType.INFO.value)
