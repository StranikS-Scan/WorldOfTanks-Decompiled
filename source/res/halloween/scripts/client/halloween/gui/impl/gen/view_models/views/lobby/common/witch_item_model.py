# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/witch_item_model.py
from halloween.gui.impl.gen.view_models.views.lobby.common.phase_item_model import PhaseItemModel

class WitchItemModel(PhaseItemModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WitchItemModel, self).__init__(properties=properties, commands=commands)

    def getIsNew(self):
        return self._getBool(4)

    def setIsNew(self, value):
        self._setBool(4, value)

    def getProgress(self):
        return self._getNumber(5)

    def setProgress(self, value):
        self._setNumber(5, value)

    def getAmount(self):
        return self._getNumber(6)

    def setAmount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(WitchItemModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('amount', 0)
