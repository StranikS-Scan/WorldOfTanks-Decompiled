# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/vehicles_sidebar/customization_3D_attachments.py
from frameworks.wulf import ViewModel

class Customization3DAttachments(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(Customization3DAttachments, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getAmount(self):
        return self._getNumber(1)

    def setAmount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(Customization3DAttachments, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('amount', 0)
