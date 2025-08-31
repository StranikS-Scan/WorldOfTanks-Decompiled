# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/base_event_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BaseEventModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=2, commands=1):
        super(BaseEventModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(BaseEventModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addResourceProperty('title', R.invalid())
        self.onAction = self._addCommand('onAction')
