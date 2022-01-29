# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/envelopes_entry_point_model.py
from frameworks.wulf import ViewModel

class EnvelopesEntryPointModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EnvelopesEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getEnvelopesCount(self):
        return self._getNumber(0)

    def setEnvelopesCount(self, value):
        self._setNumber(0, value)

    def getHasNew(self):
        return self._getBool(1)

    def setHasNew(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(EnvelopesEntryPointModel, self)._initialize()
        self._addNumberProperty('envelopesCount', 0)
        self._addBoolProperty('hasNew', False)
