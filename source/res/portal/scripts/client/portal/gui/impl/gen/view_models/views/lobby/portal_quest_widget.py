# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_quest_widget.py
from frameworks.wulf import ViewModel

class PortalQuestWidget(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PortalQuestWidget, self).__init__(properties=properties, commands=commands)

    def getCurrent(self):
        return self._getNumber(0)

    def setCurrent(self, value):
        self._setNumber(0, value)

    def getMax(self):
        return self._getNumber(1)

    def setMax(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PortalQuestWidget, self)._initialize()
        self._addNumberProperty('current', 0)
        self._addNumberProperty('max', 10)
