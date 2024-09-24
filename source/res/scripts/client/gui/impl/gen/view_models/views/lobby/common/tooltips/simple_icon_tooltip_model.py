# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/tooltips/simple_icon_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class HeaderType(Enum):
    NORMAL = 'normal'
    ATTENTION = 'attention'
    ALERT = 'alert'
    BLOCKER = 'blocker'


class SimpleIconTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SimpleIconTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getHeader(self):
        return self._getString(1)

    def setHeader(self, value):
        self._setString(1, value)

    def getBody(self):
        return self._getString(2)

    def setBody(self, value):
        self._setString(2, value)

    def getHeaderType(self):
        return HeaderType(self._getString(3))

    def setHeaderType(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(SimpleIconTooltipModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('header', '')
        self._addStringProperty('body', '')
        self._addStringProperty('headerType')
