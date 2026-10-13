# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_token_model.py
from frameworks.wulf import ViewModel

class PortalTokenModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PortalTokenModel, self).__init__(properties=properties, commands=commands)

    def getRazlomTokenCount(self):
        return self._getNumber(0)

    def setRazlomTokenCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(PortalTokenModel, self)._initialize()
        self._addNumberProperty('razlomTokenCount', 0)
