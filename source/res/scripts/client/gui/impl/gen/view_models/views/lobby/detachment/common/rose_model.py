# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/rose_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_sheet_model import RoseSheetModel

class RoseModel(ViewModel):
    __slots__ = ()
    MAX_POINTS = 100

    def __init__(self, properties=1, commands=0):
        super(RoseModel, self).__init__(properties=properties, commands=commands)

    def getSheets(self):
        return self._getArray(0)

    def setSheets(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(RoseModel, self)._initialize()
        self._addArrayProperty('sheets', Array())
