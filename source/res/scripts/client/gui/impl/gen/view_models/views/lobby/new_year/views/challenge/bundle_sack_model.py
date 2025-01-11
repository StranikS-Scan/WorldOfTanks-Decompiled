# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/bundle_sack_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SackState(Enum):
    AVAILABLE = 'available'
    RECEIVED = 'received'
    LOCKED = 'locked'


class BundleSackModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BundleSackModel, self).__init__(properties=properties, commands=commands)

    def getBundleType(self):
        return self._getString(0)

    def setBundleType(self, value):
        self._setString(0, value)

    def getSackState(self):
        return SackState(self._getString(1))

    def setSackState(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(BundleSackModel, self)._initialize()
        self._addStringProperty('bundleType', '')
        self._addStringProperty('sackState')
