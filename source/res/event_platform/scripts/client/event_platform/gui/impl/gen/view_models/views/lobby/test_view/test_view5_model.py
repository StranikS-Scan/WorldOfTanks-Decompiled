# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/gen/view_models/views/lobby/test_view/test_view5_model.py
from frameworks.wulf import ViewModel

class TestView5Model(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TestView5Model, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getString(0)

    def setHeader(self, value):
        self._setString(0, value)

    def getBody(self):
        return self._getString(1)

    def setBody(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(TestView5Model, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('body', '')
