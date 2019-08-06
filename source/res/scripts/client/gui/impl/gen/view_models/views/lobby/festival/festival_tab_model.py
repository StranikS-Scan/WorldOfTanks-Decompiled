# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_tab_model.py
from frameworks.wulf import ViewModel

class FestivalTabModel(ViewModel):
    __slots__ = ()

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getUnseenCount(self):
        return self._getNumber(1)

    def setUnseenCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(FestivalTabModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('unseenCount', 0)
