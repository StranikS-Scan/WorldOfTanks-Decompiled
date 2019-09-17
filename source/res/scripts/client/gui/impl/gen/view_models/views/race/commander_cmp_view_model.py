# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/commander_cmp_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CommanderCmpViewModel(ViewModel):
    __slots__ = ()

    def getFirstName(self):
        return self._getString(0)

    def setFirstName(self, value):
        self._setString(0, value)

    def getLastName(self):
        return self._getString(1)

    def setLastName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(CommanderCmpViewModel, self)._initialize()
        self._addStringProperty('firstName', '')
        self._addStringProperty('lastName', '')
        self._addStringProperty('description', '')
        self._addResourceProperty('icon', R.invalid())
