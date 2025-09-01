# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tab_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class TabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TabModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(TabModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addResourceProperty('title', R.invalid())
