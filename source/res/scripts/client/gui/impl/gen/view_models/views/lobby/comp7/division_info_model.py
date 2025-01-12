# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/division_info_model.py
from gui.impl.gen.view_models.views.lobby.comp7.enums import Division
from frameworks.wulf import ViewModel

class DivisionInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DivisionInfoModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return Division(self._getNumber(0))

    def setName(self, value):
        self._setNumber(0, value.value)

    def getFrom(self):
        return self._getNumber(1)

    def setFrom(self, value):
        self._setNumber(1, value)

    def getTo(self):
        return self._getNumber(2)

    def setTo(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(DivisionInfoModel, self)._initialize()
        self._addNumberProperty('name')
        self._addNumberProperty('from', 0)
        self._addNumberProperty('to', 0)
