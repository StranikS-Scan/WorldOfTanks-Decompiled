# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/meta_stats_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.meta_stats_card_model import MetaStatsCardModel

class MetaStatsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MetaStatsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getCards(self):
        return self._getArray(1)

    def setCards(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(MetaStatsViewModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)
        self._addArrayProperty('cards', Array())
